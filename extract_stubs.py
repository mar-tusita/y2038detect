#!/usr/bin/env python3
"""
extract_stubs.py — extract minimal C stub definitions from system headers.

Extracts typedefs, struct/union definitions, function declarations, extern
variables (via libclang AST), and simple integer constant macros (via
clang -E -dM).  Intended to run on a real Linux or FreeBSD system to
generate or refresh stub files under _stubs_linux/ or _stubs_freebsd/.

Usage:
    python extract_stubs.py [--outdir DIR] [--no-macros] HEADER [HEADER ...]

Examples:
    # Extract time.h and sys/types.h on Linux
    python extract_stubs.py --outdir _stubs_linux time.h sys/types.h

    # Extract sched.h for gap analysis (compare with _stubs/sched.h)
    python extract_stubs.py --outdir /tmp/extracted sched.h
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import clang.cindex as ci

# Matches simple integer or hex constant macros, e.g.:
#   #define CLOCK_REALTIME   0
#   #define O_RDONLY         0x0000
#   #define SIZE_MAX         0xffffffffffffffffULL
_RE_INT_MACRO = re.compile(
    r'^#define\s+([A-Za-z_]\w*)\s+((?:0[xX][0-9a-fA-F]+|\d+)[ULul]*)\s*$'
)

# Matches cast-wrapped integer constants, e.g.:
#   #define IPPROTO_TCP  ((int) 6)
#   #define O_NONBLOCK   ((__uint32_t) 0x0004)
_RE_CAST_MACRO = re.compile(
    r'^#define\s+([A-Za-z_]\w*)\s+\((?:\([^)*]+\)\s*)?((?:0[xX][0-9a-fA-F]+|\d+)[ULul]*)\)\s*$'
)

# Matches bit-shift constants, e.g.:
#   #define TFD_TIMER_ABSTIME   (1 << 0)
#   #define EPOLLONESHOT        (1u << 30)
_RE_SHIFT_MACRO = re.compile(
    r'^#define\s+([A-Za-z_]\w*)\s+\((\d+)[Uu]?\s*<<\s*(\d+)\)\s*$'
)

# Matches self-referential defines that expose enum constants, e.g.:
#   #define EPOLLIN EPOLLIN   (glibc wraps enum EPOLL_EVENTS values this way)
_RE_SELF_REF_MACRO = re.compile(r'^#define\s+([A-Za-z_]\w*)\s+\1\s*$')

# Macros starting with these prefixes are compiler/platform internals — skip.
# '_' covers all single- and double-underscore prefixes (e.g. _BITS_*, _LP64, __GLIBC*).
_MACRO_SKIP_PREFIXES = ('_', 'UINT', 'INT', 'SIG_')


def find_header_path(tu, header_name):
    """Return the absolute path of the directly-included header in the TU."""
    target_suffix = header_name.replace('/', Path.joinpath.__doc__ and '/')  # normalize
    for inc in tu.get_includes():
        if inc.depth != 1:
            continue
        p = inc.include.name
        if p.endswith(header_name) or Path(p).name == Path(header_name).name:
            return p
    return None


def _resolve_spelling(type_obj):
    """Return a concrete type spelling, resolving internal __ typedefs via canonical.

    If the type contains '__' (e.g. __time_t, __syscall_slong_t) and the
    canonical form is clean (no '__'), use the canonical spelling instead.
    Struct/union types whose canonical form still contains '__' are left as-is.
    """
    s = type_obj.spelling
    if '__' not in s:
        return s
    canon = type_obj.get_canonical().spelling
    return canon if '__' not in canon else s


def _field_decls(struct_cursor):
    """Return list of 'type name' strings for fields of a struct/union cursor."""
    fields = []
    for child in struct_cursor.get_children():
        if child.kind == ci.CursorKind.FIELD_DECL:
            t = _resolve_spelling(child.type)
            name = child.spelling
            if '[' in t:
                # e.g. type spelling "uint8_t [28]" -> "uint8_t name[28]"
                base, suffix = t.split('[', 1)
                fields.append(f'{base.rstrip()} {name}[{suffix}')
            else:
                fields.append(f'{t} {name}')
    return fields


def cursor_to_c(cursor, emitted_structs):
    """Convert a cursor to a C declaration string, or None to skip.

    emitted_structs: set of struct/union names already written (to avoid
    duplicating struct definitions that also appear via a typedef).
    """
    kind = cursor.kind

    if kind == ci.CursorKind.TYPEDEF_DECL:
        name = cursor.spelling
        underlying = cursor.underlying_typedef_type
        decl_cursor = underlying.get_declaration()

        # typedef to an anonymous struct/union: emit inline definition
        if (decl_cursor.kind in (ci.CursorKind.STRUCT_DECL, ci.CursorKind.UNION_DECL)
                and not decl_cursor.spelling):
            kw = 'struct' if decl_cursor.kind == ci.CursorKind.STRUCT_DECL else 'union'
            fields = _field_decls(decl_cursor)
            if fields:
                body = '\n'.join(f'    {f};' for f in fields)
                return f'typedef {kw} {{\n{body}\n}} {name};'
            return f'typedef {kw} {{}} {name};'

        # typedef to a named struct/union that will be emitted separately
        if (decl_cursor.kind in (ci.CursorKind.STRUCT_DECL, ci.CursorKind.UNION_DECL)
                and decl_cursor.spelling):
            return f'typedef {underlying.spelling} {name};'

        # simple typedef (e.g. typedef long time_t; typedef void (*fn_t)(int);)
        return f'typedef {_resolve_spelling(underlying)} {name};'

    elif kind in (ci.CursorKind.STRUCT_DECL, ci.CursorKind.UNION_DECL):
        name = cursor.spelling
        if not name:
            return None  # anonymous without a typedef — handled above
        if name in emitted_structs:
            return None  # already emitted via a typedef
        kw = 'struct' if kind == ci.CursorKind.STRUCT_DECL else 'union'
        if not cursor.is_definition():
            emitted_structs.add(name)
            return f'{kw} {name};'
        fields = _field_decls(cursor)
        emitted_structs.add(name)
        if fields:
            body = '\n'.join(f'    {f};' for f in fields)
            return f'{kw} {name} {{\n{body}\n}};'
        return f'{kw} {name};'

    elif kind == ci.CursorKind.FUNCTION_DECL:
        name = cursor.spelling
        result_t = _resolve_spelling(cursor.result_type)
        params = [_resolve_spelling(p.type) + (f' {p.spelling}' if p.spelling else '')
                  for p in cursor.get_arguments()]
        if cursor.type.kind == ci.TypeKind.FUNCTIONPROTO and cursor.type.is_function_variadic():
            params.append('...')
        params_str = ', '.join(params) if params else 'void'
        return f'{result_t} {name}({params_str});'

    elif kind == ci.CursorKind.VAR_DECL:
        if cursor.storage_class == ci.StorageClass.EXTERN:
            if cursor.spelling.startswith('_'):
                return None  # internal name (e.g. __timezone, __daylight)
            return f'extern {cursor.type.spelling} {cursor.spelling};'

    return None


def extract_ast(header_name, index):
    """Parse header with libclang and return list of C declaration strings."""
    tu = index.parse(
        'dummy.c',
        args=['-x', 'c', '-std=c11'],
        unsaved_files=[('dummy.c', f'#include <{header_name}>\n')],
    )

    if tu is None:
        print(f'  error: libclang could not parse <{header_name}>', file=sys.stderr)
        return []

    header_file = find_header_path(tu, header_name)
    if header_file is None:
        print(f'  warning: <{header_name}> not found in include tree '
              f'(no system headers on this platform?)', file=sys.stderr)
        return []

    # Pass 1: collect target-header cursors; note struct/union names referenced
    # in function declarations so we can pull their definitions from sub-includes.
    header_cursors = []
    referenced_structs = set()
    for cursor in tu.cursor.get_children():
        if cursor.location.file is None:
            continue
        if cursor.location.file.name != header_file:
            continue
        header_cursors.append(cursor)
        if cursor.kind == ci.CursorKind.FUNCTION_DECL:
            for t in [cursor.result_type] + [p.type for p in cursor.get_arguments()]:
                for m in re.finditer(r'\b(?:struct|union)\s+(\w+)',
                                     t.get_canonical().spelling):
                    referenced_structs.add(m.group(1))

    declarations = []
    seen = set()
    emitted_structs = set()

    # Pass 2: pull struct/union *definitions* from sub-includes for referenced names.
    # These must come before the function declarations that use them.
    for cursor in tu.cursor.get_children():
        if cursor.location.file is None:
            continue
        if cursor.location.file.name == header_file:
            continue  # handled in pass 3
        if cursor.kind not in (ci.CursorKind.STRUCT_DECL, ci.CursorKind.UNION_DECL):
            continue
        if not cursor.spelling or cursor.spelling not in referenced_structs:
            continue
        if not cursor.is_definition():
            continue
        decl = cursor_to_c(cursor, emitted_structs)
        if decl and decl not in seen:
            seen.add(decl)
            declarations.append(decl)

    # Pass 3: declarations from the target header itself.
    for cursor in header_cursors:
        decl = cursor_to_c(cursor, emitted_structs)
        if decl and decl not in seen:
            seen.add(decl)
            declarations.append(decl)

    return declarations


def extract_macros(header_name):
    """Return list of (name, value) for simple integer constant macros."""
    src = f'#include <{header_name}>\n'
    try:
        result = subprocess.run(
            ['clang', '-E', '-dM', '-x', 'c', '-'],
            input=src, capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f'  warning: clang -E failed: {e}', file=sys.stderr)
        return []

    macros = []
    for line in result.stdout.splitlines():
        m = _RE_INT_MACRO.match(line) or _RE_CAST_MACRO.match(line)
        if m:
            name, value = m.group(1), m.group(2)
        else:
            m = _RE_SHIFT_MACRO.match(line)
            if not m:
                continue
            name = m.group(1)
            value = hex(int(m.group(2)) << int(m.group(3)))
        if any(name.startswith(p) for p in _MACRO_SKIP_PREFIXES):
            continue
        # Skip compiler predefined macros like 'linux', 'unix' (lowercase names).
        if any(c.islower() for c in name):
            continue
        macros.append((name, value))
    return macros


def extract_enum_macros(header_name, index):
    """Return (name, hex_value) for enum constants exposed via #define NAME NAME."""
    src = f'#include <{header_name}>\n'

    # Step 1: collect self-referential defines from preprocessor output.
    try:
        result = subprocess.run(
            ['clang', '-E', '-dM', '-x', 'c', '-'],
            input=src, capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f'  warning: clang -E failed: {e}', file=sys.stderr)
        return []

    self_refs = set()
    for line in result.stdout.splitlines():
        m = _RE_SELF_REF_MACRO.match(line)
        if not m:
            continue
        name = m.group(1)
        if any(name.startswith(p) for p in _MACRO_SKIP_PREFIXES):
            continue
        if any(c.islower() for c in name):
            continue
        self_refs.add(name)

    if not self_refs:
        return []

    # Step 2: resolve values via AST (enum constants are in sub-includes,
    # so we walk the full TU without location filtering).
    tu = index.parse(
        'dummy.c',
        args=['-x', 'c', '-std=c11'],
        unsaved_files=[('dummy.c', src)],
    )
    if tu is None:
        return []

    found = {}
    for cursor in tu.cursor.walk_preorder():
        if cursor.kind != ci.CursorKind.ENUM_CONSTANT_DECL:
            continue
        name = cursor.spelling
        if name not in self_refs or name in found:
            continue
        val = cursor.enum_value
        # Represent as unsigned hex (handles sign-extended 32-bit flags like EPOLLET).
        found[name] = hex(val & 0xFFFFFFFF) if val < 0 else hex(val)

    return list(found.items())


def write_stub(header_name, outdir, declarations, macros):
    """Write extracted declarations and macros to a stub file."""
    out_path = Path(outdir) / header_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    guard = re.sub(r'[^A-Za-z0-9]', '_', header_name).upper() + '_STUB'

    lines = [
        f'/* Generated by extract_stubs.py from <{header_name}> */',
        f'/* Review carefully before committing — do not blindly overwrite existing stubs */',
        f'#ifndef {guard}',
        f'#define {guard}',
        '',
    ]

    if declarations:
        lines += declarations
        lines.append('')

    if macros:
        for name, val in sorted(macros):
            lines.append(f'#define {name}  {val}')
        lines.append('')

    lines.append(f'#endif /* {guard} */')

    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  wrote {out_path}  '
          f'({len(declarations)} decls, {len(macros)} macros)', file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description='Extract minimal C stub definitions from system headers.',
        epilog='Run on a real Linux or FreeBSD system, not on Windows.',
    )
    p.add_argument('headers', nargs='+', metavar='HEADER',
                   help='Header name(s) to process, e.g. time.h sys/types.h')
    p.add_argument('--outdir', '-o', default='extracted',
                   help='Output directory (default: extracted/)')
    p.add_argument('--no-macros', action='store_true',
                   help='Skip macro extraction via clang -E -dM')
    args = p.parse_args()

    index = ci.Index.create()

    for header in args.headers:
        print(f'Processing <{header}> ...', file=sys.stderr)
        decls = extract_ast(header, index)
        if args.no_macros:
            macros = []
        else:
            macros = extract_macros(header) + extract_enum_macros(header, index)
        if not decls and not macros:
            print(f'  (nothing extracted — skipping)', file=sys.stderr)
            continue
        write_stub(header, args.outdir, decls, macros)


if __name__ == '__main__':
    main()
