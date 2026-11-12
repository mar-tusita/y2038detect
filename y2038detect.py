#!/usr/bin/env python3
"""y2038 problem detector: finds time_t narrowing conversions in C source."""

from _version import __version__

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import deque, namedtuple
from functools import lru_cache

try:
    import tomllib
except ImportError:
    tomllib = None  # Python 3.10: config file support unavailable

import clang.cindex
from clang.cindex import CursorKind, TypeKind

# Bundled minimal stubs — searched last, as a fallback when no system headers
# are available (e.g. no compiler installed).
_STUBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_stubs')

# Matches "y2038: ignore" (case-insensitive, optional spaces around colon)
# in both // and /* */ comment styles.
# Negative lookahead (?!-) prevents matching "ignore-begin" and "ignore-end".
_IGNORE_RE       = re.compile(r'y2038\s*:\s*ignore(?!-)',     re.IGNORECASE)
_IGNORE_BEGIN_RE = re.compile(r'y2038\s*:\s*ignore-begin',    re.IGNORECASE)
_IGNORE_END_RE   = re.compile(r'y2038\s*:\s*ignore-end',      re.IGNORECASE)


# CXTranslationUnit_KeepGoing (libclang >= 9): do not stop processing after a
# fatal error such as an unresolvable #include. The Python bindings don't
# expose it as a named constant. Without it clang drops later diagnostics
# (including the -Wformat ones the printf check depends on).
_PARSE_KEEP_GOING = 0x200


# On Windows, MinGW headers define struct timespec conditionally and may
# omit types that our stubs guarantee.  Skip auto-detection there; users
# can still add paths via -I.
_COMPILERS = () if sys.platform == 'win32' else ('gcc', 'clang', 'cc')


@lru_cache(maxsize=1)
def _compiler_includes() -> tuple:
    """Return system C include paths from the first available compiler.

    Tries compilers in _COMPILERS order.  Parses the verbose preprocessor
    output to extract the '#include <...> search' list.  Result is cached
    for the lifetime of the process.
    """
    for compiler in _COMPILERS:
        if not shutil.which(compiler):
            continue
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.c', mode='w',
                                             delete=False) as f:
                f.write('')
                tmp = f.name
            result = subprocess.run(
                [compiler, '-x', 'c', '-v', '-E', tmp],
                capture_output=True, text=True, timeout=10)
            paths = []
            in_section = False
            for line in result.stderr.splitlines():
                if '#include <...> search starts here' in line:
                    in_section = True
                    continue
                if 'End of search list' in line:
                    break
                if in_section:
                    path = line.strip()
                    if os.path.isdir(path):
                        paths.append(path)
            if paths:
                return tuple(paths)
        except Exception:
            pass
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
    return ()

Issue = namedtuple('Issue', ['file', 'line', 'col', 'message'])

_TIME_TYPEDEFS = frozenset({'time_t'})

# Divisors that semantically represent time units.  A time_t value reduced
# by % with one of these is guaranteed to fit in int, so narrowing afterward
# is not a 2038 problem. 7 (days per week, e.g. day-of-week computations
# like (days+4)%7) is included alongside the second/minute/hour/day/week
# divisors for the same reason.
_TIME_UNIT_DIVISORS = frozenset({7, 60, 3600, 86400, 604800})

_NARROW_INT_KINDS = frozenset({
    TypeKind.BOOL,
    TypeKind.CHAR_U,  TypeKind.UCHAR,
    TypeKind.CHAR_S,  TypeKind.SCHAR,
    TypeKind.SHORT,   TypeKind.USHORT,
    TypeKind.INT,     TypeKind.UINT,
    TypeKind.LONG,    TypeKind.ULONG,
})

# struct tm: tm_year is years since 1900.  2038 - 1900 = 138.
_TM_YEAR_2038 = 138
# Don't flag values below year 2000 (tm_year < 100): those are typically
# Y2K-era 2-digit-year hacks, not 2038-related boundaries.
_TM_YEAR_MIN  = 100

# Maximum value of a 32-bit signed time_t (2038-01-19 03:14:07 UTC).
_TIME_T_INT32_MAX = 0x7FFFFFFF  # 2147483647

# libclang diagnostic category for printf-family format/argument type mismatches.
_PRINTF_FORMAT_DIAG_CATEGORY = 31

# struct stat timestamp fields.  Accessing these fields signals use of
# filesystem timestamps, which may be limited to 32 bits on some filesystems
# (ext2/3, pre-5.10 XFS, etc.) regardless of the in-memory type.
# Both the legacy time_t fields and the modern timespec fields are included.
_STAT_TIME_FIELDS = frozenset({
    'st_mtime', 'st_atime', 'st_ctime',  # time_t  (POSIX legacy)
    'st_mtim',  'st_atim',  'st_ctim',   # struct timespec (POSIX.1-2008)
})

# Filesystem timestamp-setting APIs.
# Deprecated APIs (utime/utimes/lutimes/futimes) use time_t or struct timeval
# with a 32-bit-range tv_sec and are flagged by default.
# Modern APIs (utimensat/futimens) use struct timespec but are still limited
# on 32-bit systems; flagged only under --strict.
_FS_TIMESTAMP_DEPRECATED_FUNCS = frozenset({'utime', 'utimes', 'lutimes', 'futimes'})
_FS_TIMESTAMP_MODERN_FUNCS     = frozenset({'utimensat', 'futimens'})

# Functions where a time_t-derived value is used as a seed or similar
# opaque quantity, never as an actual calendar-time value (e.g.
# srand(time(NULL))). Narrowing such a value is safe when it is the
# direct Nth argument (0-based, per the frozenset of positions below) of
# one of these calls, so it is suppressed like other bounded cases.
_TIME_SINK_FUNCS = {
    'srand':     frozenset({0}),
    'srandom':   frozenset({0}),
    'initstate': frozenset({0}),
    'srand48':   frozenset({0}),
}


def _is_time_type(t: clang.cindex.Type) -> bool:
    """Return True if t is time_t or any typedef that resolves to time_t.

    A cv-qualified reference (e.g. a `const time_t` variable) has its
    qualifiers included in .spelling ("const time_t"), which would never
    match _TIME_TYPEDEFS by exact string comparison. Strip leading
    "const "/"volatile " before comparing, since a variable's qualifiers
    don't change whether its underlying type is time_t.
    """
    seen = set()
    while True:
        name = t.spelling
        while True:
            if name.startswith('const '):
                name = name[len('const '):]
            elif name.startswith('volatile '):
                name = name[len('volatile '):]
            else:
                break
        if name in _TIME_TYPEDEFS:
            return True
        if name in seen:
            break
        seen.add(name)
        decl = t.get_declaration()
        if decl.kind != CursorKind.TYPEDEF_DECL:
            break
        t = decl.underlying_typedef_type
    return False


def _type_kind(t: clang.cindex.Type):
    """Return t.kind, or None if the Python bindings don't know this TypeKind.

    libclang itself can report type kinds newer than the Python bindings
    that ship alongside it; Type.kind then raises ValueError. The pip
    libclang 18.1.1 bindings, for example, don't list CXType_Float16 (32),
    so any use of _Float16 crashed the whole scan. None never matches a
    real TypeKind, so callers treat an unknown type as "not the type I am
    looking for" instead of failing.
    """
    try:
        return t.kind
    except ValueError:
        return None


def _is_narrow_int(t: clang.cindex.Type, strict: bool = False) -> bool:
    size = t.get_size()
    if size <= 0:
        return False
    kind = _type_kind(t.get_canonical())
    if kind not in _NARROW_INT_KINDS:
        return False
    if strict and kind in (TypeKind.LONG, TypeKind.ULONG):
        return True  # always flag long/unsigned long regardless of platform size
    return size < 8


def _truncation_year(dest: clang.cindex.Type) -> str:
    """Return the year a time_t value narrowed to dest actually overflows.

    Unsigned 32-bit destinations (uint32_t, unsigned int, or a typedef that
    canonicalizes to one of them, e.g. JFFS2's jint32_t) wrap at 2^32
    seconds since epoch (2106), not the signed 32-bit boundary (2038) the
    message otherwise assumes. Narrower unsigned types (uint16_t etc.)
    overflow almost immediately after epoch, not at a meaningful future
    calendar year, so they are deliberately left saying 2038 rather than
    a technically-correct but confusing "1970".
    """
    if _type_kind(dest.get_canonical()) in (TypeKind.UINT, TypeKind.ULONG) and dest.get_size() == 4:
        return '2106'
    return '2038'


def _contains_tm_year(cursor: clang.cindex.Cursor, cache: dict = None) -> bool:
    """Return True if cursor or any descendant is a tm_year member access.

    cache memoizes by cursor (Cursor implements __hash__/__eq__ against the
    underlying AST node, so this is safe) across the whole _walk() of one
    file. Without it, a chain of N nested BINARY_OPERATORs (e.g. flag masks
    combined with repeated `|`, as in GNU binutils-style opcode tables) costs
    O(N^2) node visits: _walk()'s own traversal visits each nested operator
    as a node in its own right, and each one's _check_tm_year_ceiling() call
    used to rescan its entire operand subtree from scratch, even though an
    ancestor operator's check had already just scanned right through it.
    This turned one real file (radare2's ppc-opc.c) into a ~1200s outlier
    in an otherwise fast scan; see CHANGELOG/TODO.
    """
    if cache is not None and cursor in cache:
        return cache[cursor]
    if cursor.kind == CursorKind.MEMBER_REF_EXPR and cursor.spelling == 'tm_year':
        result = True
    else:
        result = any(_contains_tm_year(c, cache) for c in cursor.get_children())
    if cache is not None:
        cache[cursor] = result
    return result


def _tu_has_tm_year(cursor: clang.cindex.Cursor) -> bool:
    """Return True if cursor's subtree contains a tm_year member access
    anywhere (not restricted to the scanned file), short-circuiting as soon
    as one is found.

    _check_tm_year_ceiling() can only ever match a BINARY_OPERATOR whose
    operand subtree contains a tm_year MEMBER_REF_EXPR, and the overwhelming
    majority of C files have none at all. _walk() calls this once per file
    so it can skip _check_tm_year_ceiling() (and its _contains_tm_year()
    subtree scans) entirely for those files instead of paying a per-
    BINARY_OPERATOR cost that can never find a match -- a single file with
    a very large number of unrelated BINARY_OPERATOR nodes (radare2's
    ppc-opc.c, a GNU binutils-style opcode table combining flags with `|`)
    turned that per-node cost into a ~1200s outlier in an otherwise fast
    scan even after _contains_tm_year() itself was memoized (see CHANGELOG/
    TODO). Checking the whole TU rather than just the scanned file's own
    text is deliberate: a tm_year access reached through a macro defined in
    an included header would not appear as the literal substring "tm_year"
    in the scanned file, so a source-text check could miss it; this walks
    the actual (post-preprocessing) AST instead, so it cannot under-detect.
    """
    stack = deque([cursor])
    while stack:
        node = stack.pop()
        if node.kind == CursorKind.MEMBER_REF_EXPR and node.spelling == 'tm_year':
            return True
        stack.extend(node.get_children())
    return False


_RE_DECIMAL = re.compile(r'^\d+$')
_RE_HEX     = re.compile(r'^0[xX][0-9a-fA-F]+$')


def _int_literal_value(cursor: clang.cindex.Cursor) -> int | None:
    """Return the integer value of an INTEGER_LITERAL cursor, or None.

    Handles both plain literals (138) and macro-expanded values where the
    token list may include surrounding parentheses, e.g. #define LIM (138).
    Also handles hex literals such as 0x7FFFFFFF.
    """
    if cursor.kind == CursorKind.INTEGER_LITERAL:
        for tok in cursor.get_tokens():
            if _RE_DECIMAL.match(tok.spelling):
                return int(tok.spelling)
            if _RE_HEX.match(tok.spelling):
                return int(tok.spelling, 16)
    elif cursor.kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.PAREN_EXPR):
        children = list(cursor.get_children())
        if children:
            return _int_literal_value(children[0])
    return None


def _binary_op(cursor: clang.cindex.Cursor) -> str | None:
    """Return the operator token of a BINARY_OPERATOR cursor, or None."""
    children = list(cursor.get_children())
    if len(children) < 2:
        return None
    left_end    = children[0].extent.end.offset
    right_start = children[1].extent.start.offset
    for tok in cursor.get_tokens():
        if tok.extent.start.offset >= left_end and tok.extent.end.offset <= right_start:
            return tok.spelling
    return None


_CMP_OPS = frozenset({'<', '<=', '==', '>=', '>'})


def _check_time_t_max_comparison(cursor: clang.cindex.Cursor, loc, issues: list) -> None:
    """Flag comparisons of time_t with 0x7FFFFFFF (32-bit time_t maximum)."""
    children = list(cursor.get_children())
    if len(children) != 2:
        return
    left, right = children

    # Cheap necessary-condition check before the expensive literal
    # extraction below: an implicit widening cast makes the 0x7FFFFFFF
    # literal ITSELF report as time_t-typed too (see the next comment), so
    # a real match always has at least one time_t-typed side. Skipping
    # early when neither side is saves _int_literal_value()'s
    # cursor.get_tokens() tokenize call (expensive; ~1-2ms) for the
    # overwhelming majority of BINARY_OPERATOR nodes in a typical file,
    # which have nothing to do with time_t at all. This does not change
    # which side ends up chosen below -- it is a pure early-exit on a
    # condition the original match already implies.
    if not (_is_time_type(left.type) or _is_time_type(right.type)):
        return

    # Identify which side is the integer literal 0x7FFFFFFF.  We try the
    # literal extraction first because an implicit widening cast wraps the
    # literal in UNEXPOSED_EXPR(time_t), making both sides look like time_t.
    right_val = _int_literal_value(right)
    left_val  = _int_literal_value(left)

    if right_val == _TIME_T_INT32_MAX:
        time_side = left
    elif left_val == _TIME_T_INT32_MAX:
        time_side = right
    else:
        return

    if not _is_time_type(time_side.type):
        return

    op = _binary_op(cursor)
    if op not in _CMP_OPS:
        return

    issues.append(Issue(
        file=str(loc.file),
        line=loc.line,
        col=loc.column,
        message=("time_t compared with 0x7FFFFFFF (2^31-1): "
                 "assumes 32-bit time_t, will misbehave after 2038"),
    ))


def _check_tm_year_ceiling(cursor: clang.cindex.Cursor, loc, issues: list, strict: bool = False,
                           tm_year_cache: dict = None) -> None:
    """Flag BINARY_OPERATOR comparisons that cap tm_year at year 2038 or earlier."""
    children = list(cursor.get_children())
    if len(children) != 2:
        return
    left, right = children

    if _contains_tm_year(left, tm_year_cache):
        tm_year_is_left, lit_cursor = True, right
    elif _contains_tm_year(right, tm_year_cache):
        tm_year_is_left, lit_cursor = False, left
    else:
        return

    val = _int_literal_value(lit_cursor)
    if val is None or val > _TM_YEAR_2038:
        return
    if not strict and val < _TM_YEAR_MIN:
        return

    op = _binary_op(cursor)
    if op is None:
        return

    if tm_year_is_left:
        is_ceiling = op in ('<', '<=')
    else:
        is_ceiling = op in ('>', '>=')

    if is_ceiling:
        year = 1900 + val
        issues.append(Issue(
            file=str(loc.file),
            line=loc.line,
            col=loc.column,
            message=(f"tm_year compared with {val} (year {year}): "
                     f"upper bound excludes dates beyond {year}"),
        ))


def _collect_bounded_vars(func_cursor: clang.cindex.Cursor) -> tuple[set, dict]:
    """Pre-scan a function body for time_t variables bounded by a time-unit modulo,
    and for time_t constants declared with a literal initializer.

    Detects three patterns:
      val %= 86400                     (COMPOUND_ASSIGNMENT_OPERATOR)
      time_t seconds = expr % 86400   (VAR_DECL with BINARY_OPERATOR initializer)
      const time_t secs_hour = 3600;   (VAR_DECL with a literal or foldable
                                        arithmetic initializer, e.g. 3600*24)

    The modulo divisor in the first two patterns may itself be a named
    constant rather than a bare literal (e.g. `t % secs_day`), and that
    constant's own initializer may in turn be an arithmetic expression
    (e.g. `const time_t secs_day = 3600*24;`) rather than a bare literal.
    Constants are therefore resolved in a fixed-point first pass -- trying
    every candidate declaration repeatedly until a full pass adds nothing
    new -- before the modulo patterns are checked in a second pass. This
    handles both directions of the ordering problem: the main stack-based
    walk is LIFO (not source order), and a constant may reference another
    constant declared later in the same function.

    Returns (bounded, const_vars):
      bounded    -- variable spellings whose *value* is safe to narrow to int
      const_vars -- variable spelling -> resolved integer value, for
                    constants that aren't themselves bounded but can be used
                    elsewhere as a known-small modulo/division operand (see
                    _is_source_bounded)
    """
    const_vars: dict = {}
    const_decls: list = []
    stack: list = [func_cursor]
    while stack:
        node = stack.pop()
        if node.kind == CursorKind.VAR_DECL and _is_time_type(node.type):
            decl_ch = list(node.get_children())
            if decl_ch:
                const_decls.append((node.spelling, decl_ch[-1]))
        stack.extend(node.get_children())

    progress = True
    while progress:
        progress = False
        for name, init in const_decls:
            if name in const_vars:
                continue
            val = _fold_int_const(init, const_vars)
            if val is not None:
                const_vars[name] = val
                progress = True

    bounded: set = set()
    stack = [func_cursor]
    while stack:
        node = stack.pop()
        kind = node.kind
        if kind == CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
            op_ch = list(node.get_children())
            if (len(op_ch) == 2
                    and _is_time_type(op_ch[0].type)
                    and _binary_op(node) == '%='):
                val = _resolve_time_const(op_ch[1], const_vars)
                if val in _TIME_UNIT_DIVISORS:
                    bounded.add(op_ch[0].spelling)
        elif kind == CursorKind.VAR_DECL and _is_time_type(node.type):
            decl_ch = list(node.get_children())
            if decl_ch and decl_ch[-1].kind == CursorKind.BINARY_OPERATOR:
                init = decl_ch[-1]
                init_ch = list(init.get_children())
                if len(init_ch) == 2 and _binary_op(init) == '%':
                    val = _resolve_time_const(init_ch[1], const_vars)
                    if val in _TIME_UNIT_DIVISORS:
                        bounded.add(node.spelling)
        stack.extend(node.get_children())
    return bounded, const_vars


def _collect_time_sink_locations(func_cursor: clang.cindex.Cursor) -> set:
    """Pre-scan a function body for time_t narrowing passed directly to a
    known "time sink" function (see _TIME_SINK_FUNCS), e.g. srand(time(NULL)).

    Returns a set of (line, col) locations of the narrowing conversion
    nodes themselves, for the walker to check against when deciding
    whether to suppress a narrowing finding at that same location.
    """
    locations: set = set()
    stack: list = [func_cursor]
    while stack:
        node = stack.pop()
        if node.kind == CursorKind.CALL_EXPR:
            positions = _TIME_SINK_FUNCS.get(node.spelling)
            if positions:
                # children[0] is the callee reference; real arguments follow.
                args = list(node.get_children())[1:]
                for pos in positions:
                    if pos >= len(args):
                        continue
                    arg = args[pos]
                    if arg.kind not in (CursorKind.UNEXPOSED_EXPR, CursorKind.CSTYLE_CAST_EXPR):
                        continue
                    if not _is_narrow_int(arg.type):
                        continue
                    arg_children = [c for c in arg.get_children()
                                     if c.kind != CursorKind.TYPE_REF]
                    if arg_children and _is_time_type(arg_children[0].type):
                        loc = arg.location
                        locations.add((loc.line, loc.column))
        stack.extend(node.get_children())
    return locations


def _fold_int_const(cursor: clang.cindex.Cursor, const_vars: dict) -> int | None:
    """Recursively fold a compile-time integer constant expression.

    Handles bare literals, references to constants already recorded in
    const_vars, and +, -, *, / between two foldable operands. This lets a
    chained constant like `const time_t secs_day = 3600*24;` resolve to
    86400, so it (and expressions built from it) can be used as a
    recognised time-unit divisor elsewhere. Other operators (e.g. %) are
    deliberately not folded here -- that would blur constant-folding with
    the boundedness reasoning done by _is_source_bounded.
    """
    node = cursor
    while node.kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.PAREN_EXPR):
        children = list(node.get_children())
        if len(children) != 1:
            break
        node = children[0]
    if node.kind == CursorKind.INTEGER_LITERAL:
        return _int_literal_value(node)
    if node.kind == CursorKind.DECL_REF_EXPR:
        return const_vars.get(node.spelling)
    if node.kind == CursorKind.BINARY_OPERATOR:
        children = list(node.get_children())
        if len(children) == 2:
            op = _binary_op(node)
            if op in ('*', '+', '-', '/'):
                left = _fold_int_const(children[0], const_vars)
                right = _fold_int_const(children[1], const_vars)
                if left is not None and right is not None:
                    if op == '*':
                        return left * right
                    if op == '+':
                        return left + right
                    if op == '-':
                        return left - right
                    if right != 0:
                        return left // right
    return None


def _resolve_time_const(cursor: clang.cindex.Cursor, const_vars: dict) -> int | None:
    """Resolve cursor to an integer value if it is a literal, a reference to
    a time_t constant recorded in const_vars, or an arithmetic expression
    built from either (see _fold_int_const). Returns None if not resolvable.
    """
    return _fold_int_const(cursor, const_vars)


def _is_source_bounded(cursor: clang.cindex.Cursor, bounded_vars: set,
                        const_vars: dict = None) -> bool:
    """Return True if cursor's value is provably bounded to a small range.

    Beyond the base case (every time_t operand referenced is a variable in
    bounded_vars), two arithmetic-based extensions are recognised,
    regardless of the OTHER operand's own boundedness:

      X % N   is bounded to [0, N) whenever N resolves (via a literal, or
              a reference to a const_vars constant) to a recognised
              time-unit divisor (_TIME_UNIT_DIVISORS).
      X / Y   is bounded whenever X (the dividend) is itself bounded --
              dividing a bounded value by anything cannot make it larger.

    Both extensions are applied recursively (e.g. (seconds % secs_hour) /
    secs_min), which is safe here because expression nesting is bounded in
    practice, unlike whole-file AST depth (see _walk()'s own note on why
    *that* traversal must be iterative).
    """
    const_vars = const_vars or {}

    if cursor.kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.PAREN_EXPR):
        children = list(cursor.get_children())
        if len(children) == 1:
            return _is_source_bounded(children[0], bounded_vars, const_vars)

    elif cursor.kind == CursorKind.BINARY_OPERATOR:
        children = list(cursor.get_children())
        if len(children) == 2:
            left, right = children
            op = _binary_op(cursor)
            if op == '%':
                divisor = _resolve_time_const(right, const_vars)
                if divisor in _TIME_UNIT_DIVISORS:
                    return True
            elif op == '/':
                if _is_source_bounded(left, bounded_vars, const_vars):
                    return True

    # Fallback (and the base case for the recursion above): every time_t
    # operand referenced anywhere in this expression must itself be a
    # bounded variable.
    found_time_var = False
    stack = [cursor]
    while stack:
        node = stack.pop()
        if node.kind == CursorKind.DECL_REF_EXPR and _is_time_type(node.type):
            found_time_var = True
            if node.spelling not in bounded_vars:
                return False
        elif node.kind == CursorKind.CALL_EXPR and _is_time_type(node.type):
            return False
        stack.extend(node.get_children())
    return found_time_var


def _walk(cursor: clang.cindex.Cursor, source_path: str, issues: list, strict: bool = False) -> None:
    # Iterative traversal via an explicit stack avoids Python's recursion limit
    # (default 1000), which recursive descent could exceed on deeply nested or
    # heavily macro-expanded C code.
    stack = deque([cursor])
    # bounded_vars and time_sink_locs are pre-scanned per function via
    # _collect_bounded_vars() / _collect_time_sink_locations().
    bounded_vars: set = set()
    const_vars: dict = {}
    time_sink_locs: set = set()
    # Shared across the whole file (not reset per function): whether a
    # cursor's subtree contains a tm_year access is a purely structural
    # property, independent of which BINARY_OPERATOR ancestor is asking. See
    # _contains_tm_year()'s docstring for why this cache matters.
    tm_year_cache: dict = {}
    # Skip _check_tm_year_ceiling() entirely for the (overwhelming majority
    # of) files with no tm_year access anywhere -- see _tu_has_tm_year()'s
    # docstring.
    has_tm_year = _tu_has_tm_year(cursor)
    while stack:
        node = stack.pop()
        kind = node.kind

        # Pre-scan the whole function body for bounded variables and
        # time-sink call arguments so that the traversal order does not
        # matter (e.g. the modulo assignment may appear after the
        # narrowing in DFS order due to LIFO processing).
        if kind == CursorKind.FUNCTION_DECL:
            bounded_vars, const_vars = (set(), {}) if strict else _collect_bounded_vars(node)
            time_sink_locs = set() if strict else _collect_time_sink_locations(node)

        # UNEXPOSED_EXPR is how libclang's Python bindings expose implicit casts.
        # CSTYLE_CAST_EXPR covers explicit (int) style casts.
        elif kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.CSTYLE_CAST_EXPR):
            loc = node.location
            if loc.file and os.path.normcase(loc.file.name) == source_path:
                dest = node.type
                if _is_narrow_int(dest, strict):
                    # Casting to a *typedef'd* type (e.g. (uint32_t)x, as
                    # opposed to a builtin like (int)x) makes libclang insert
                    # a TYPE_REF child before the operand, referencing the
                    # named type used in the cast. Skip it so the operand is
                    # always the first real child regardless of cast spelling.
                    children = [c for c in node.get_children()
                                if c.kind != CursorKind.TYPE_REF]
                    if children and _is_time_type(children[0].type):
                        if not strict and _is_source_bounded(children[0], bounded_vars, const_vars):
                            pass  # provably bounded → skip
                        elif (loc.line, loc.column) in time_sink_locs:
                            pass  # direct argument to a known time sink → skip
                        else:
                            label = "implicit" if kind == CursorKind.UNEXPOSED_EXPR else "explicit"
                            issues.append(Issue(
                                file=str(loc.file),
                                line=loc.line,
                                col=loc.column,
                                message=(f"{label} conversion of time_t to '{dest.spelling}' "
                                         f"may truncate after {_truncation_year(dest)}"),
                            ))

        elif kind == CursorKind.BINARY_OPERATOR:
            loc = node.location
            if loc.file and os.path.normcase(loc.file.name) == source_path:
                if has_tm_year:
                    _check_tm_year_ceiling(node, loc, issues, strict, tm_year_cache)
                _check_time_t_max_comparison(node, loc, issues)

        elif kind == CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
            loc = node.location
            if loc.file and os.path.normcase(loc.file.name) == source_path:
                children = list(node.get_children())
                if len(children) == 2:
                    left, right = children
                    if _is_narrow_int(left.type, strict) and _is_time_type(right.type):
                        is_bounded = not strict and _is_source_bounded(right, bounded_vars, const_vars)
                        if not is_bounded:
                            issues.append(Issue(
                                file=str(loc.file),
                                line=loc.line,
                                col=loc.column,
                                message=(f"compound assignment of time_t to "
                                         f"'{left.type.spelling}' may truncate after "
                                         f"{_truncation_year(left.type)}"),
                            ))

        elif kind == CursorKind.MEMBER_REF_EXPR:
            if strict and node.spelling in _STAT_TIME_FIELDS:
                loc = node.location
                if loc.file and os.path.normcase(loc.file.name) == source_path:
                    children = list(node.get_children())
                    if children:
                        child_type = children[0].type.get_canonical()
                        if _type_kind(child_type) == TypeKind.POINTER:
                            child_type = child_type.get_pointee().get_canonical()
                        if child_type.spelling == 'struct stat':
                            issues.append(Issue(
                                file=str(loc.file),
                                line=loc.line,
                                col=loc.column,
                                message=(
                                    f"access to struct stat timestamp field "
                                    f"'{node.spelling}': filesystem may not "
                                    f"preserve timestamps beyond 2038"
                                ),
                            ))

        stack.extend(node.get_children())


def _collect_printf_issues(tu, source_path: str, issues: list) -> None:
    """Collect time_t format-string mismatches from libclang diagnostics.

    libclang reports printf-family format/argument type mismatches as category
    31 ('Format String Issue').  We filter for messages that mention 'time_t':
    those indicate a time_t value was passed with a format specifier whose
    expected type is narrower (e.g. %d expects int on all platforms).
    """
    for diag in tu.diagnostics:
        if diag.category_number != _PRINTF_FORMAT_DIAG_CATEGORY:
            continue
        if 'time_t' not in diag.spelling:
            continue
        loc = diag.location
        if not loc.file:
            continue
        if os.path.normcase(loc.file.name) != source_path:
            continue
        issues.append(Issue(
            file=str(loc.file),
            line=loc.line,
            col=loc.column,
            message=(
                "time_t passed to printf-family function with incompatible "
                "format specifier: may truncate after 2038"
            ),
        ))


def _collect_fs_timestamp_issues(tu, source_path: str, issues: list,
                                  strict: bool = False) -> None:
    """Collect calls to filesystem timestamp-setting APIs.

    Deprecated APIs (utime/utimes/lutimes/futimes) are flagged by default
    because they use time_t or struct timeval whose tv_sec is limited to
    the 32-bit range.  Modern POSIX replacements (utimensat/futimens) are
    flagged only under --strict because they are the recommended APIs but
    still affected on 32-bit systems.
    """
    _DEPRECATED_MSGS = {
        'utime':   ("call to utime() uses time_t timestamps; "
                    "limited to 32-bit range — use utimensat() instead"),
        'utimes':  ("call to utimes() uses struct timeval with long tv_sec; "
                    "limited to 32-bit range — use utimensat() instead"),
        'lutimes': ("call to lutimes() uses struct timeval with long tv_sec; "
                    "limited to 32-bit range — use utimensat() instead"),
        'futimes': ("call to futimes() uses struct timeval with long tv_sec; "
                    "limited to 32-bit range — use futimens() instead"),
    }
    stack = deque([tu.cursor])
    while stack:
        node = stack.pop()
        if node.kind == CursorKind.CALL_EXPR:
            name = node.spelling
            loc  = node.location
            if loc.file and os.path.normcase(loc.file.name) == source_path:
                if name in _FS_TIMESTAMP_DEPRECATED_FUNCS:
                    issues.append(Issue(
                        file=str(loc.file), line=loc.line, col=loc.column,
                        message=_DEPRECATED_MSGS[name],
                    ))
                elif strict and name in _FS_TIMESTAMP_MODERN_FUNCS:
                    issues.append(Issue(
                        file=str(loc.file), line=loc.line, col=loc.column,
                        message=(f"call to {name}() may set timestamps limited "
                                 f"to 32-bit time_t on 32-bit systems"),
                    ))
        stack.extend(node.get_children())


def _parse_tu(path: str, extra_args=None, system_includes: bool = True):
    """Return (TranslationUnit, normalized_source_path), or (None, None) on failure."""
    abspath = os.path.abspath(path)
    # Order: user args → system headers (skipped with --no-system-includes) → stubs
    system_incs = [f'-I{p}' for p in _compiler_includes()] if system_includes else []
    args = list(extra_args or []) + system_incs + [f'-I{_STUBS_DIR}', '-Wformat', '-ferror-limit=0']
    tu = clang.cindex.Index.create().parse(abspath, args=args, options=_PARSE_KEEP_GOING)
    return tu, os.path.normcase(abspath)


def _report_diagnostics(tu, show_diagnostics: bool, always_report_fatal: bool = False) -> bool:
    """Print libclang diagnostics to stderr; return True if any was Fatal.

    Nothing here stops the analysis: the AST that libclang returns after an
    error (typically an unresolvable #include) is still usable, and
    v0.9.3's evaluation lost ~90% of its files by giving up at that point.
    show_diagnostics prints both "fatal:" and "parse error:" lines;
    always_report_fatal prints "fatal:" lines even without it.
    """
    had_fatal = False
    for diag in tu.diagnostics:
        if diag.severity == clang.cindex.Diagnostic.Fatal:
            had_fatal = True
            if show_diagnostics or always_report_fatal:
                print(f"fatal: {diag.spelling}", file=sys.stderr)
        elif diag.severity == clang.cindex.Diagnostic.Error and show_diagnostics:
            print(f"parse error: {diag.spelling}", file=sys.stderr)
    return had_fatal


def _filter_suppressed(issues: list, path: str) -> list:
    """Remove issues suppressed by y2038: ignore (per-line) or ignore-begin/end blocks."""
    if not issues:
        return issues
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            src_lines = f.readlines()
    except OSError:
        return issues

    suppressed = set()
    in_range = False
    for i, line in enumerate(src_lines, 1):
        if _IGNORE_BEGIN_RE.search(line):
            in_range = True
        if in_range or _IGNORE_RE.search(line):
            suppressed.add(i)
        if _IGNORE_END_RE.search(line):
            in_range = False

    return [issue for issue in issues if issue.line not in suppressed]


def _extract_args_from_entry(entry: dict) -> list:
    """Extract libclang-relevant flags (-I, -D, -std=, -isystem) from one compile_commands entry."""
    directory = entry.get('directory', '')
    if 'arguments' in entry:
        tokens = list(entry['arguments'])
    elif 'command' in entry:
        try:
            # posix=False avoids treating backslash as an escape character,
            # which is necessary for Windows paths (e.g. C:\Users\...).
            # Surrounding quotes are preserved in this mode, so strip them.
            tokens = shlex.split(entry['command'], posix=False)
            tokens = [
                tok[1:-1] if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in '"\''
                else tok
                for tok in tokens
            ]
        except ValueError:
            return []
    else:
        return []
    if tokens:
        tokens = tokens[1:]  # skip compiler executable

    def _resolve(path):
        if not os.path.isabs(path) and directory:
            path = os.path.join(directory, path)
        return os.path.normpath(path)

    result = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith('-I') and len(tok) > 2:
            result.append(f'-I{_resolve(tok[2:])}')
        elif tok == '-I' and i + 1 < len(tokens):
            result.append(f'-I{_resolve(tokens[i + 1])}')
            i += 1
        elif tok.startswith('-D') and len(tok) > 2:
            result.append(tok)
        elif tok == '-D' and i + 1 < len(tokens):
            result.append(f'-D{tokens[i + 1]}')
            i += 1
        elif tok.startswith('-std='):
            result.append(tok)
        elif tok == '-isystem' and i + 1 < len(tokens):
            result.extend(['-isystem', _resolve(tokens[i + 1])])
            i += 1
        i += 1
    return result


def load_compile_commands(path: str) -> dict:
    """Load compile_commands.json; return {normalized_file_path: [extra_args]}.

    Returns an empty dict if the file cannot be read or parsed.
    """
    try:
        with open(path, encoding='utf-8') as f:
            db = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    result = {}
    for entry in db:
        file_path = entry.get('file', '')
        if not file_path:
            continue
        directory = entry.get('directory', '')
        if not os.path.isabs(file_path) and directory:
            file_path = os.path.join(directory, file_path)
        norm = os.path.normcase(os.path.abspath(file_path))
        result[norm] = _extract_args_from_entry(entry)
    return result


def scan(path: str, extra_args=None, system_includes: bool = True, strict: bool = False,
         show_diagnostics: bool = False) -> list:
    """Parse C file and return list of Issue namedtuples (no output).

    show_diagnostics=True prints libclang parse errors (including fatal
    ones) to stderr. It does not change the result: a file with parse
    errors is still analyzed.
    """
    tu, source_path = _parse_tu(path, extra_args, system_includes=system_includes)
    if tu is None:
        return []
    _report_diagnostics(tu, show_diagnostics)
    issues = []
    _walk(tu.cursor, source_path, issues, strict=strict)
    _collect_printf_issues(tu, source_path, issues)
    _collect_fs_timestamp_issues(tu, source_path, issues, strict=strict)
    return _filter_suppressed(issues, os.path.abspath(path))


def _scan_dual(path: str, extra_args=None, system_includes: bool = True,
               show_diagnostics: bool = False) -> tuple:
    """Parse once; return (default_issues, strict_issues) in a single AST pass.

    Shares the _parse_tu() call so the file is parsed only once regardless
    of how many detection modes are run.
    """
    tu, source_path = _parse_tu(path, extra_args, system_includes=system_includes)
    if tu is None:
        return [], []
    _report_diagnostics(tu, show_diagnostics)
    return _collect_dual(tu, source_path, path)


def _collect_dual(tu, source_path: str, path: str) -> tuple:
    """Run the default and strict detection passes over an already-parsed TU.

    Split out of _scan_dual() so a caller that parses for its own purposes
    (evaluation/scripts/11_report_file_status.py inspects the diagnostics)
    can reuse the parse instead of doing it twice.
    """
    def _collect(strict):
        issues = []
        _walk(tu.cursor, source_path, issues, strict=strict)
        _collect_printf_issues(tu, source_path, issues)
        _collect_fs_timestamp_issues(tu, source_path, issues, strict=strict)
        return _filter_suppressed(issues, os.path.abspath(path))

    return _collect(False), _collect(True)


def _github_annotation_path(abspath: str) -> str:
    """Return a path relative to GITHUB_WORKSPACE (or CWD as fallback).

    GitHub Actions requires annotation file paths to be relative to the
    workspace root; absolute paths are silently ignored by the runner.
    """
    base = os.environ.get('GITHUB_WORKSPACE') or os.getcwd()
    try:
        return os.path.relpath(abspath, base).replace(os.sep, '/')
    except ValueError:
        return abspath.replace(os.sep, '/')


def _read_source_lines(abspath: str) -> list | None:
    """Return abspath's lines (readlines(), newline included), or None if unreadable."""
    try:
        with open(abspath, encoding='utf-8', errors='replace') as f:
            return f.readlines()
    except OSError:
        return None


def _source_context_from_lines(lines: list, line: int, before: int = 6, after: int = 2) -> list:
    """Return the lines around *line* as [{"line": N, "text": ...}, ...].

    Line numbers are clamped to the file's actual extent, so a flagged line
    near the start or end of the file yields a shorter list rather than
    going out of range.

    before=6/after=2 is a magic number carried over from make_scan_log.py's
    extract_code_context() (its own defaults, undocumented reasoning) to
    keep the two functions' output looking the same in
    evaluation/scripts/05_generate_findings.py. Confirmed with the user
    (2026-09-28) that this asymmetry can be changed if a real reason comes
    up; if it is, update both functions' defaults together.
    """
    first = max(1, line - before)
    last  = min(len(lines), line + after)
    return [{'line': n, 'text': lines[n - 1].rstrip('\n')} for n in range(first, last + 1)]


def _source_context(abspath: str, line: int, before: int = 6, after: int = 2) -> list | None:
    """Return the source lines around *line*, or None if abspath can no longer
    be read (e.g. removed since it was scanned). See _source_context_from_lines()."""
    lines = _read_source_lines(abspath)
    if lines is None:
        return None
    return _source_context_from_lines(lines, line, before, after)


def _display_path(abspath: str) -> str:
    """Return a CWD-relative path for display; fall back to abspath if outside CWD.

    Paths that would require leading '..' (i.e. outside the current working
    directory) or cross drive roots on Windows are returned as-is.
    """
    try:
        rel = os.path.relpath(abspath, os.getcwd())
        if rel.startswith('..'):
            return abspath
        return rel
    except ValueError:
        return abspath


_ANSI_BOLD        = '\x1b[1m'
_ANSI_YELLOW_BOLD = '\x1b[1;33m'
_ANSI_GREEN       = '\x1b[32m'
_ANSI_YELLOW      = '\x1b[33m'
_ANSI_RESET       = '\x1b[0m'


def _colorize(text: str, code: str, enabled: bool) -> str:
    return f'{code}{text}{_ANSI_RESET}' if enabled else text


def analyze(path: str, extra_args=None, fmt: str = 'default',
            absolute: bool = False, color: bool = False,
            system_includes: bool = True, strict: bool = False,
            show_diagnostics: bool = False) -> int:
    """Parse C file, print warnings with source context, return exit code.

    fmt='default' prints GCC-style warnings with a source-line excerpt.
    fmt='github'  prints GitHub Actions workflow commands (::warning ::).
    absolute=True uses absolute paths; False (default) uses CWD-relative paths.
    color=True    adds ANSI color codes (only used with fmt='default').
    show_diagnostics=True also prints non-fatal libclang parse errors to stderr
    (fatal ones are always printed). Parse errors never stop the analysis.
    """
    tu, source_path = _parse_tu(path, extra_args, system_includes=system_includes)
    if tu is None:
        print(f"error: cannot parse '{path}'", file=sys.stderr)
        return 1

    had_fatal = _report_diagnostics(tu, show_diagnostics, always_report_fatal=True)

    issues = []
    _walk(tu.cursor, source_path, issues, strict=strict)
    _collect_printf_issues(tu, source_path, issues)
    _collect_fs_timestamp_issues(tu, source_path, issues, strict=strict)
    issues = _filter_suppressed(issues, os.path.abspath(path))

    if not issues:
        # A libclang Fatal diagnostic that survived KeepGoing still makes
        # the run non-zero (as documented), without counting as an issue.
        return 1 if had_fatal else 0

    if fmt == 'github':
        for issue in issues:
            fpath = _github_annotation_path(issue.file)
            print(f"::warning file={fpath},line={issue.line},"
                  f"col={issue.col}::{issue.message}")
    else:
        try:
            with open(os.path.abspath(path), encoding='utf-8', errors='replace') as f:
                src_lines = f.readlines()
        except OSError:
            src_lines = []

        for issue in issues:
            dpath = issue.file if absolute else _display_path(issue.file)
            loc   = _colorize(f"{dpath}:{issue.line}:{issue.col}:", _ANSI_BOLD, color)
            label = _colorize("warning:", _ANSI_YELLOW_BOLD, color)
            print(f"{loc} {label} {issue.message}")
            if src_lines and 1 <= issue.line <= len(src_lines):
                print(f"  {src_lines[issue.line - 1].rstrip()}")
                caret = _colorize('^', _ANSI_GREEN, color)
                print(f"  {' ' * (issue.col - 1)}{caret}")

    return len(issues)


def _is_excluded(path: str, patterns: list) -> bool:
    """Return True if path matches any --exclude pattern.

    Patterns are matched against the full path with forward slashes.
    A pattern without a leading slash is also tried with a '*/' prefix so
    that 'vendor/*' matches 'src/vendor/foo.c' without the caller needing
    to write '*/vendor/*'.
    """
    norm = path.replace(os.sep, '/')
    for pat in patterns:
        if fnmatch.fnmatch(norm, pat):
            return True
        if not pat.startswith('/') and fnmatch.fnmatch(norm, '*/' + pat):
            return True
    return False


def _find_config() -> dict:
    """Search CWD and parent directories for pyproject.toml with [tool.y2038detect].

    Stops at the first pyproject.toml found (whether or not it has the section).
    Prints a note to stderr when a non-empty section is found.
    Returns an empty dict when tomllib is unavailable (Python 3.10).
    """
    if tomllib is None:
        return {}
    directory = os.path.abspath(os.getcwd())
    while True:
        candidate = os.path.join(directory, 'pyproject.toml')
        if os.path.isfile(candidate):
            try:
                with open(candidate, 'rb') as f:
                    data = tomllib.load(f)
                section = data.get('tool', {}).get('y2038detect', {})
                if section:
                    print(f"note: using config from {candidate}", file=sys.stderr)
                return section
            except Exception:
                return {}
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return {}


def _collect_paths(paths: list, exclude: list = None) -> list:
    """Expand directory arguments to .c files recursively; keep file paths as-is.

    Files discovered via directory expansion are filtered against *exclude*
    patterns.  Paths given explicitly on the command line are never excluded.
    """
    excl = exclude or []
    result = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.endswith('.c'):
                        full = os.path.join(root, f)
                        if not _is_excluded(full, excl):
                            result.append(full)
        elif os.path.isfile(p):
            result.append(p)
        else:
            print(f"error: not found: '{p}'", file=sys.stderr)
    return result


def _report_file_error(path: str, exc: Exception) -> None:
    """Report an unexpected failure while scanning one file.

    The "internal error:" prefix is stable: evaluation/scripts/02_scan.py
    counts lines starting with it. (A libclang parse error is different and
    is printed as "parse error:" / "fatal:".)
    """
    print(f"internal error: {path}: {type(exc).__name__}: {exc}", file=sys.stderr)


def _exit_code(has_issues: bool, failed_files: int) -> int:
    """0 = clean, 1 = issues found, 2 = some file could not be analyzed.

    2 takes precedence over 1: an incomplete analysis must never look like
    a normal result, even if the files that did work had issues.
    """
    if failed_files:
        return 2
    return 1 if has_issues else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='y2038detect',
        description='Detect Year 2038 problems in C source files.')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('paths', nargs='+', metavar='PATH',
                        help='C source files or directories to scan')
    parser.add_argument('-I', dest='includes', action='append', default=[],
                        metavar='DIR', help='add compiler include search path')
    parser.add_argument('-D', dest='defines', action='append', default=[],
                        metavar='MACRO',
                        help='define preprocessor macro (e.g. -DFOO or -DFOO=1)')
    parser.add_argument('-U', dest='undefines', action='append', default=[],
                        metavar='MACRO',
                        help='undefine preprocessor macro (e.g. -U_WIN32)')
    parser.add_argument('--target', dest='target', metavar='TRIPLE', default=None,
                        help='target triple passed to libclang '
                             '(e.g. x86_64-pc-linux-gnu); '
                             'changes predefined macros and type sizes')
    parser.add_argument('-X', dest='clang_flags', action='append', default=[],
                        metavar='FLAG',
                        help='pass FLAG directly to libclang (may be repeated; '
                             'use = to attach values starting with -: '
                             '-X=-ferror-limit=0 -X=-std=c11)')
    parser.add_argument('--json', action='store_true',
                        help='output results as JSON array')
    parser.add_argument('--compile-commands', dest='compile_commands',
                        metavar='FILE',
                        help='path to compile_commands.json (per-file -I/-D flags)')
    parser.add_argument('--exclude', dest='exclude', action='append', default=[],
                        metavar='PATTERN',
                        help='exclude files matching PATTERN from directory scans '
                             '(fnmatch; may be repeated)')
    parser.add_argument('--format', dest='fmt', choices=['default', 'github'],
                        default=None,
                        help='output format: "default" (GCC-style) or "github" '
                             '(GitHub Actions annotations); '
                             'auto-detected from GITHUB_ACTIONS env var when omitted')
    parser.add_argument('--absolute', action='store_true',
                        help='display file paths as absolute paths '
                             '(default: CWD-relative)')
    parser.add_argument('--no-system-includes', dest='no_system_includes',
                        action='store_true',
                        help='skip compiler auto-detected system headers; '
                             'use bundled stubs only')
    parser.add_argument('--show-parse-errors', dest='show_parse_errors',
                        action='store_true',
                        help='print non-fatal libclang parse errors to stderr '
                             '(default: suppressed)')
    parser.add_argument('--strict', action='store_true',
                        help='disable all heuristic suppressions and enable extra checks: '
                             'report long/unsigned long narrowing regardless of platform size, '
                             'flag all tm_year comparisons (including Y2K-era hacks), '
                             'report bounded-variable narrowing, '
                             'flag struct stat filesystem timestamp field accesses, '
                             'and flag calls to utimensat()/futimens()')
    parser.add_argument('--with-strict', dest='with_strict', action='store_true',
                        help='run both without and with --strict in a single pass; '
                             'outputs {"default":[...], "strict":[...]} JSON '
                             '(requires --json; cannot be combined with --strict)')
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument('--color', dest='color', action='store_true', default=False,
                             help='force color output')
    color_group.add_argument('--no-color', dest='no_color', action='store_true', default=False,
                             help='disable color output')
    args = parser.parse_args()

    if args.with_strict and args.strict:
        parser.error('--with-strict and --strict are mutually exclusive')
    if args.with_strict and not args.json:
        parser.error('--with-strict requires --json')

    config = _find_config()
    if not args.compile_commands and 'compile_commands' in config:
        args.compile_commands = str(config['compile_commands'])
    if 'exclude' in config:
        args.exclude = list(config['exclude']) + args.exclude
    if 'includes' in config:
        args.includes = list(config['includes']) + args.includes
    if config.get('strict') and not args.strict:
        args.strict = True
    if 'extra_clang_args' in config:
        args.clang_flags = list(config['extra_clang_args']) + args.clang_flags

    extra_args  = [f'-I{d}' for d in args.includes]
    extra_args += [f'-D{m}' for m in args.defines]
    extra_args += [f'-U{m}' for m in args.undefines]
    if args.target:
        extra_args += ['-target', args.target]
    extra_args += args.clang_flags
    paths = _collect_paths(args.paths, exclude=args.exclude)

    if not paths:
        sys.exit(1)

    compile_db = {}
    if args.compile_commands:
        compile_db = load_compile_commands(args.compile_commands)
        if not compile_db:
            print(f"warning: '{args.compile_commands}': no entries loaded",
                  file=sys.stderr)

    def _file_args(path):
        norm = os.path.normcase(os.path.abspath(path))
        return extra_args + compile_db.get(norm, [])

    if args.json:
        source_lines_cache = {}

        def _context_for(i):
            if i.file not in source_lines_cache:
                source_lines_cache[i.file] = _read_source_lines(i.file)
            lines = source_lines_cache[i.file]
            return None if lines is None else _source_context_from_lines(lines, i.line)

        def _fmt_issues(issues):
            return [{'file': i.file if args.absolute else _display_path(i.file),
                     'line': i.line, 'col': i.col, 'message': i.message,
                     'context': _context_for(i)}
                    for i in issues]

        if args.with_strict:
            default_issues = []
            strict_issues = []
            failed_files = 0
            for path in paths:
                try:
                    d, s = _scan_dual(path, _file_args(path),
                                      system_includes=not args.no_system_includes,
                                      show_diagnostics=args.show_parse_errors)
                except Exception as e:
                    _report_file_error(path, e)
                    failed_files += 1
                    continue
                default_issues.extend(d)
                strict_issues.extend(s)
            print(json.dumps(
                {'default': _fmt_issues(default_issues),
                 'strict':  _fmt_issues(strict_issues)},
                indent=2))
            sys.exit(_exit_code(bool(default_issues or strict_issues), failed_files))

        all_issues = []
        failed_files = 0
        for path in paths:
            try:
                all_issues.extend(scan(path, _file_args(path),
                                       system_includes=not args.no_system_includes,
                                       strict=args.strict,
                                       show_diagnostics=args.show_parse_errors))
            except Exception as e:
                _report_file_error(path, e)
                failed_files += 1
        print(json.dumps(_fmt_issues(all_issues), indent=2))
        sys.exit(_exit_code(bool(all_issues), failed_files))

    if args.fmt is not None:
        fmt = args.fmt
    elif os.environ.get('GITHUB_ACTIONS') == 'true':
        fmt = 'github'
    else:
        fmt = 'default'

    if args.no_color or os.environ.get('NO_COLOR') is not None:
        color = False
    elif args.color:
        color = True
    else:
        color = sys.stdout.isatty()

    total_issues = 0
    files_with_issues = 0
    failed_files = 0
    for path in paths:
        try:
            n = analyze(path, _file_args(path), fmt=fmt, absolute=args.absolute, color=color,
                        system_includes=not args.no_system_includes, strict=args.strict,
                        show_diagnostics=args.show_parse_errors)
        except Exception as e:
            _report_file_error(path, e)
            failed_files += 1
            continue
        if n > 0:
            files_with_issues += 1
            total_issues += n

    if len(paths) > 1:
        clean = len(paths) - files_with_issues - failed_files
        if total_issues == 0 and failed_files == 0:
            line = f"All {len(paths)} files clean."
            print(_colorize(line, _ANSI_GREEN, color))
        else:
            si = '' if total_issues == 1 else 's'
            sf = '' if files_with_issues == 1 else 's'
            line = f"{total_issues} issue{si} in {files_with_issues} file{sf} ({clean} clean)"
            if failed_files:
                line += f", {failed_files} not analyzed (internal error)"
            print(_colorize(line, _ANSI_YELLOW, color))

    sys.exit(_exit_code(total_issues > 0, failed_files))


if __name__ == '__main__':
    main()
