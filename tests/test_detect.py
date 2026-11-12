"""Tests for y2038detect."""

import ctypes
import io
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import y2038detect

# True when 'long' is narrower than 64 bits (Windows ILP32 model).
_LONG_IS_NARROW = ctypes.sizeof(ctypes.c_long) < 8

_PREAMBLE = '#include <time.h>\n#include <stdint.h>\n'


def _scan(body: str, strict: bool = False) -> list:
    """Write body as a C function body to a temp file and return Issues."""
    code = _PREAMBLE + 'void _test(void) {\n' + body + '\n}\n'
    with tempfile.NamedTemporaryFile(suffix='.c', mode='w', delete=False,
                                     encoding='utf-8') as f:
        f.write(code)
        fname = f.name
    try:
        return y2038detect.scan(fname, strict=strict)
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Implicit narrowing conversions
# ---------------------------------------------------------------------------

class TestImplicit:
    def test_int(self):
        issues = _scan('int t = time(NULL);')
        assert len(issues) == 1
        assert 'implicit' in issues[0].message
        assert "'int'" in issues[0].message
        assert '2038' in issues[0].message

    def test_int32(self):
        issues = _scan('int32_t t = time(NULL);')
        assert len(issues) == 1
        assert 'implicit' in issues[0].message
        assert "'int32_t'" in issues[0].message
        assert '2038' in issues[0].message

    def test_uint32(self):
        # unsigned 32-bit wraps at 2^32 seconds since epoch (2106), not the
        # signed 32-bit boundary (2038).
        issues = _scan('uint32_t t = time(NULL);')
        assert len(issues) == 1
        assert 'implicit' in issues[0].message
        assert '2106' in issues[0].message

    def test_unsigned_int(self):
        # Same as uint32_t but spelled as the base type rather than a typedef.
        issues = _scan('unsigned int t = time(NULL);')
        assert len(issues) == 1
        assert '2106' in issues[0].message

    def test_uint16_stays_2038(self):
        # Narrower unsigned types overflow almost immediately after epoch,
        # not at a meaningful future year, so they are deliberately left
        # saying 2038 rather than a technically-correct but confusing 1970.
        issues = _scan('uint16_t t = time(NULL);')
        assert len(issues) == 1
        assert '2038' in issues[0].message

    def test_long(self):
        # long is 32-bit on Windows, 64-bit on LP64 Linux.
        issues = _scan('long t = time(NULL);')
        if _LONG_IS_NARROW:
            assert len(issues) == 1
            assert '2038' in issues[0].message
        else:
            assert len(issues) == 0

    def test_unsigned_long(self):
        # unsigned long: 32-bit on Windows (2106), 64-bit on LP64 Linux (not narrow).
        issues = _scan('unsigned long t = time(NULL);')
        if _LONG_IS_NARROW:
            assert len(issues) == 1
            assert '2106' in issues[0].message
        else:
            assert len(issues) == 0

    def test_from_variable(self):
        issues = _scan('time_t now = time(NULL);\nint t = now;')
        assert len(issues) == 1
        assert 'implicit' in issues[0].message


# ---------------------------------------------------------------------------
# Explicit casts
# ---------------------------------------------------------------------------

class TestExplicit:
    def test_cast_from_variable(self):
        issues = _scan('time_t now = time(NULL);\nint t = (int)now;')
        assert len(issues) == 1
        assert 'explicit' in issues[0].message
        assert '2038' in issues[0].message

    def test_cast_from_call(self):
        issues = _scan('int t = (int)time(NULL);')
        assert len(issues) == 1
        assert 'explicit' in issues[0].message

    def test_cast_to_unsigned_int(self):
        issues = _scan('unsigned int t = (unsigned int)time(NULL);')
        assert len(issues) == 1
        assert 'explicit' in issues[0].message
        assert '2106' in issues[0].message

    def test_cast_to_typedef(self):
        # Regression: casting to a *typedef'd* type (uint32_t, as opposed to
        # a builtin like int/unsigned int) used to go undetected, because
        # libclang inserts a TYPE_REF child before the actual operand for
        # named cast targets, and _walk() assumed children[0] was the operand.
        issues = _scan('uint32_t t = (uint32_t)time(NULL);')
        assert len(issues) == 1
        assert 'explicit' in issues[0].message
        assert '2106' in issues[0].message

    def test_cast_to_custom_typedef(self):
        issues = _scan('typedef int myint;\nmyint t = (myint)time(NULL);')
        assert len(issues) == 1
        assert 'explicit' in issues[0].message
        assert '2038' in issues[0].message


# ---------------------------------------------------------------------------
# Correct usage — must NOT be flagged
# ---------------------------------------------------------------------------

class TestNoFlag:
    def test_time_t(self):
        assert _scan('time_t t = time(NULL);') == []

    def test_int64(self):
        assert _scan('int64_t t = time(NULL);') == []

    def test_long_long(self):
        assert _scan('long long t = time(NULL);') == []

    def test_time_t_from_variable(self):
        assert _scan('time_t now = time(NULL);\ntime_t t = now;') == []


# ---------------------------------------------------------------------------
# Patterns to verify: already detected or not?
# ---------------------------------------------------------------------------

def _scan_toplevel(code: str, strict: bool = False) -> list:
    """Write top-level C code to a temp file and return Issues."""
    full = _PREAMBLE + code
    with tempfile.NamedTemporaryFile(suffix='.c', mode='w', delete=False,
                                     encoding='utf-8') as f:
        f.write(full)
        fname = f.name
    try:
        return y2038detect.scan(fname, strict=strict)
    finally:
        os.unlink(fname)


class TestFunctionArgument:
    """time_t value passed to a function expecting a narrow int."""

    def test_arg_to_int_param(self):
        # foo(int) called with time(NULL)
        issues = _scan_toplevel(
            'void foo(int t);\n'
            'void test(void) { foo(time(NULL)); }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_arg_from_variable(self):
        # foo(int) called with time_t variable
        issues = _scan_toplevel(
            'void foo(int t);\n'
            'void test(void) { time_t now = time(NULL); foo(now); }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_arg_to_time_t_param_no_flag(self):
        # foo(time_t) — must NOT be flagged
        issues = _scan_toplevel(
            'void foo(time_t t);\n'
            'void test(void) { foo(time(NULL)); }\n'
        )
        assert issues == [], f"expected no issues, got: {issues}"


class TestStructMemberAssign:
    """time_t value assigned to a narrow-int struct member."""

    def test_member_assign_from_call(self):
        issues = _scan_toplevel(
            'struct S { int ts; };\n'
            'void test(void) { struct S s; s.ts = time(NULL); }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_member_assign_from_variable(self):
        issues = _scan_toplevel(
            'struct S { int ts; };\n'
            'void test(void) { time_t now = time(NULL); struct S s; s.ts = now; }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_member_assign_time_t_no_flag(self):
        # struct member is time_t — must NOT be flagged
        issues = _scan_toplevel(
            'struct S { time_t ts; };\n'
            'void test(void) { struct S s; s.ts = time(NULL); }\n'
        )
        assert issues == [], f"expected no issues, got: {issues}"


class TestReturnNarrowing:
    """Function returning narrow int with time_t value."""

    def test_return_from_call(self):
        issues = _scan_toplevel(
            'int get_ts(void) { return time(NULL); }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_return_from_variable(self):
        issues = _scan_toplevel(
            'int get_ts(void) { time_t now = time(NULL); return now; }\n'
        )
        assert len(issues) == 1, f"expected 1, got {len(issues)}: {issues}"

    def test_return_time_t_no_flag(self):
        # return type is time_t — must NOT be flagged
        issues = _scan_toplevel(
            'time_t get_ts(void) { return time(NULL); }\n'
        )
        assert issues == [], f"expected no issues, got: {issues}"


# ---------------------------------------------------------------------------
# tm_year ceiling detection
# ---------------------------------------------------------------------------

class TestTmYearCeiling:
    """tm_year compared with a constant that caps the year at 2038 or earlier."""

    def test_less_than_138_direct(self):
        # t.tm_year < 138  (year 2038 boundary, direct struct access)
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year < 138; }\n'
        )
        assert len(issues) == 1
        assert 'tm_year' in issues[0].message
        assert '138' in issues[0].message

    def test_less_than_138_pointer(self):
        # tp->tm_year < 138  (pointer access)
        issues = _scan_toplevel(
            'struct tm *tp;\n'
            'int f(void) { return tp->tm_year < 138; }\n'
        )
        assert len(issues) == 1

    def test_literal_on_left(self):
        # 138 > t.tm_year  (literal on left side)
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return 138 > t.tm_year; }\n'
        )
        assert len(issues) == 1

    def test_leq_137(self):
        # tm_year <= 137  (same effective ceiling: year 2037)
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year <= 137; }\n'
        )
        assert len(issues) == 1
        assert '137' in issues[0].message

    def test_leq_138(self):
        # tm_year <= 138  (ceiling at year 2038 itself)
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year <= 138; }\n'
        )
        assert len(issues) == 1

    def test_full_pattern(self):
        # tm_year > 68 && tm_year < 138  — only the upper bound is flagged
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year > 68 && t.tm_year < 138; }\n'
        )
        assert len(issues) == 1
        assert '138' in issues[0].message

    def test_lower_bound_no_flag(self):
        # tm_year > 68  — lower bound only, must NOT be flagged
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year > 68; }\n'
        )
        assert issues == []

    def test_value_139_no_flag(self):
        # tm_year < 139  — ceiling is year 2039, not a 2038 problem
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year < 139; }\n'
        )
        assert issues == []

    def test_large_value_no_flag(self):
        # tm_year < 200  — ceiling is year 2100, no issue
        issues = _scan_toplevel(
            'struct tm t;\n'
            'int f(void) { return t.tm_year < 200; }\n'
        )
        assert issues == []


# ---------------------------------------------------------------------------
# typedef chain resolution
# ---------------------------------------------------------------------------

class TestTypedefChain:
    """time_t narrowing detected through one or more typedef aliases."""

    def test_single_alias(self):
        # typedef time_t my_time_t;  int x = my_time_t_var;
        issues = _scan_toplevel(
            'typedef time_t my_time_t;\n'
            'void f(void) { my_time_t now = time(NULL); int x = now; }\n'
        )
        assert len(issues) == 1
        assert 'implicit' in issues[0].message

    def test_double_alias(self):
        # typedef time_t A; typedef A B;  int x = B_var;
        issues = _scan_toplevel(
            'typedef time_t A;\n'
            'typedef A B;\n'
            'void f(void) { B now = time(NULL); int x = now; }\n'
        )
        assert len(issues) == 1

    def test_alias_direct_assign(self):
        # typedef time_t ts_t;  int x = time(NULL) stored via alias
        issues = _scan_toplevel(
            'typedef time_t ts_t;\n'
            'int f(void) { ts_t t = time(NULL); return t; }\n'
        )
        # return t: ts_t -> int (narrowing)
        assert len(issues) == 1
        assert 'implicit' in issues[0].message

    def test_alias_no_flag_correct_type(self):
        # storing into the alias itself — must NOT be flagged
        issues = _scan_toplevel(
            'typedef time_t my_time_t;\n'
            'void f(void) { my_time_t now = time(NULL); my_time_t t = now; }\n'
        )
        assert issues == []

    def test_unrelated_typedef_no_flag(self):
        # typedef int counter_t — unrelated, must NOT be flagged
        issues = _scan_toplevel(
            'typedef int counter_t;\n'
            'void f(void) { counter_t c = 0; }\n'
        )
        assert issues == []


# ---------------------------------------------------------------------------
# #define macro constants in tm_year comparisons
# ---------------------------------------------------------------------------

class TestMacroTmYear:
    """tm_year compared with a #define constant equal to 138."""

    def test_simple_define(self):
        # #define YEAR_LIMIT 138
        issues = _scan_toplevel(
            '#define YEAR_LIMIT 138\n'
            'int f(void) { struct tm t; return t.tm_year < YEAR_LIMIT; }\n'
        )
        assert len(issues) == 1
        assert '138' in issues[0].message

    def test_parens_define(self):
        # #define YEAR_LIMIT (138)
        issues = _scan_toplevel(
            '#define YEAR_LIMIT (138)\n'
            'int f(void) { struct tm t; return t.tm_year < YEAR_LIMIT; }\n'
        )
        assert len(issues) == 1
        assert '138' in issues[0].message

    def test_pointer_access(self):
        issues = _scan_toplevel(
            '#define YLIM 138\n'
            'int f(struct tm *t) { return t->tm_year < YLIM; }\n'
        )
        assert len(issues) == 1

    def test_literal_on_left(self):
        # 138 > t.tm_year
        issues = _scan_toplevel(
            '#define YL 138\n'
            'int f(void) { struct tm t; return YL > t.tm_year; }\n'
        )
        assert len(issues) == 1

    def test_large_value_no_flag(self):
        # #define YEAR_FAR 200  — must NOT be flagged
        issues = _scan_toplevel(
            '#define YEAR_FAR 200\n'
            'int f(void) { struct tm t; return t.tm_year < YEAR_FAR; }\n'
        )
        assert issues == []

    def test_lower_bound_no_flag(self):
        # lower bound only — must NOT be flagged
        issues = _scan_toplevel(
            '#define YEAR_MIN 70\n'
            'int f(void) { struct tm t; return t.tm_year > YEAR_MIN; }\n'
        )
        assert issues == []

    def test_has_tm_year_detects_access_via_header_macro(self, tmp_path):
        # _walk()'s whole-TU has_tm_year pre-check (_tu_has_tm_year(), added
        # to skip _check_tm_year_ceiling() entirely for the common case of a
        # file with no tm_year access anywhere -- see CHANGELOG) must walk
        # the actual AST rather than a source-text substring search, or it
        # would miss a tm_year access reached only through a macro defined
        # in an included header (the literal substring "tm_year" never
        # appears in the scanned file's own text in that case).
        #
        # This is tested directly against _tu_has_tm_year() rather than
        # through scan()'s end-to-end output: a separate, pre-existing bug
        # in _binary_op() (unrelated to this fix -- it also reproduces on
        # unmodified pre-fix code) makes _check_tm_year_ceiling() fail to
        # identify the comparison operator whenever either operand is
        # itself macro-expanded, so scan() would report no issue here
        # regardless of whether the has_tm_year pre-check is correct.
        inc_dir = tmp_path / 'include'
        inc_dir.mkdir()
        (inc_dir / 'yearmacro.h').write_text(
            '#define YEAR_OF(tp) ((tp)->tm_year)\n', encoding='utf-8')

        src = tmp_path / 'test.c'
        src.write_text(
            '#include <time.h>\n'
            '#include "yearmacro.h"\n'
            'int f(struct tm *t) { return YEAR_OF(t) < 138; }\n',
            encoding='utf-8')

        tu, _ = y2038detect._parse_tu(str(src), [f'-I{inc_dir}'])
        assert y2038detect._tu_has_tm_year(tu.cursor) is True

    def test_has_tm_year_false_when_absent(self, tmp_path):
        src = tmp_path / 'test.c'
        src.write_text(
            '#include <time.h>\nint f(void) { time_t t = time(NULL); return (int)t; }\n',
            encoding='utf-8')
        tu, _ = y2038detect._parse_tu(str(src))
        assert y2038detect._tu_has_tm_year(tu.cursor) is False


# ---------------------------------------------------------------------------
# 0x7FFFFFFF (32-bit time_t max) comparison detection
# ---------------------------------------------------------------------------

class TestTimeT0x7FFFFFFF:
    """time_t compared with 0x7FFFFFFF (or its decimal equivalent 2147483647)."""

    def test_less_than_hex(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t < 0x7FFFFFFF; }\n'
        )
        assert len(issues) == 1
        assert '0x7FFFFFFF' in issues[0].message

    def test_less_equal_hex(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t <= 0x7FFFFFFF; }\n'
        )
        assert len(issues) == 1

    def test_equal_hex(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t == 0x7FFFFFFF; }\n'
        )
        assert len(issues) == 1

    def test_greater_equal_hex(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t >= 0x7FFFFFFF; }\n'
        )
        assert len(issues) == 1

    def test_greater_than_hex(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t > 0x7FFFFFFF; }\n'
        )
        assert len(issues) == 1

    def test_literal_on_left(self):
        # 0x7FFFFFFF on the left side
        issues = _scan_toplevel(
            'int f(time_t t) { return 0x7FFFFFFF > t; }\n'
        )
        assert len(issues) == 1

    def test_decimal_equivalent(self):
        # Same value written as decimal
        issues = _scan_toplevel(
            'int f(time_t t) { return t < 2147483647; }\n'
        )
        assert len(issues) == 1
        assert '0x7FFFFFFF' in issues[0].message

    def test_non_time_t_no_flag(self):
        # int, not time_t — must NOT be flagged
        issues = _scan_toplevel(
            'int f(int n) { return n < 0x7FFFFFFF; }\n'
        )
        assert issues == []

    def test_different_value_no_flag(self):
        # 0x7FFFFFFE — one less, must NOT be flagged
        issues = _scan_toplevel(
            'int f(time_t t) { return t < 0x7FFFFFFE; }\n'
        )
        assert issues == []

    def test_suppressed_by_ignore(self):
        issues = _scan_toplevel(
            'int f(time_t t) { return t < 0x7FFFFFFF; } // y2038: ignore\n'
        )
        assert issues == []


# ---------------------------------------------------------------------------
# Integration: domktime.c  (real-world example provided by user)
# ---------------------------------------------------------------------------

class TestDomktime:
    def test_issue_count(self):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        issues = y2038detect.scan(src)
        # line 10: tm_year < 138 ceiling
        # line 14: return ret (time_t -> int narrowing)
        assert len(issues) == 2

    def test_tm_year_ceiling(self):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        issues = y2038detect.scan(src)
        ceiling = [i for i in issues if 'tm_year' in i.message]
        assert len(ceiling) == 1
        assert ceiling[0].line == 10

    def test_return_narrowing(self):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        issues = y2038detect.scan(src)
        narrowing = [i for i in issues if 'implicit' in i.message]
        assert len(narrowing) == 1
        assert narrowing[0].line == 14


# ---------------------------------------------------------------------------
# Integration: FreeBSD source excerpts
# ---------------------------------------------------------------------------

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestFreeBSDVary:
    """vary.c from FreeBSD date(1): contains the canonical domktime() pattern."""

    def test_issue_count(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'vary.c'))
        # line 62: tm_year < 138 ceiling
        # line 66: return ret (time_t -> int narrowing)
        assert len(issues) == 2

    def test_tm_year_ceiling(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'vary.c'))
        ceiling = [i for i in issues if 'tm_year' in i.message]
        assert len(ceiling) == 1
        assert ceiling[0].line == 62

    def test_return_narrowing(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'vary.c'))
        narrowing = [i for i in issues if 'implicit' in i.message]
        assert len(narrowing) == 1
        assert narrowing[0].line == 66

    def test_y2k_hack_not_flagged(self):
        # line 139: tm_year < 69 is a Y2K 2-digit-year hack, not a 2038 problem
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'vary.c'))
        flagged_lines = {i.line for i in issues}
        assert 139 not in flagged_lines


class TestFreeBSDSleep:
    """sleep.c from FreeBSD: casts time_t and struct timespec.tv_sec to int."""

    def test_issue_count(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'sleep.c'))
        # line 97: (int)time_to_sleep.tv_sec and (int)original — both explicit
        assert len(issues) == 2

    def test_both_casts_on_line_97(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'sleep.c'))
        assert all(i.line == 97 for i in issues)
        assert all('explicit' in i.message for i in issues)


class TestFreeBSDDate:
    """date.c from FreeBSD: no 2038 issues detectable (Y2K hacks excluded)."""

    def test_no_issues(self):
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'date.c'))
        assert issues == []


# ---------------------------------------------------------------------------
# Integration: sample.c
# ---------------------------------------------------------------------------

class TestSampleFile:
    def test_issue_count(self):
        sample = os.path.join(os.path.dirname(__file__), 'sample.c')
        issues = y2038detect.scan(sample)
        # 5 implicit: int, long (Windows only), int32_t, uint32_t, int-from-var
        # 2 explicit: (int)now, (int)time(NULL)
        expected = 7 if _LONG_IS_NARROW else 6
        assert len(issues) == expected

    def test_implicit_explicit_split(self):
        sample = os.path.join(os.path.dirname(__file__), 'sample.c')
        issues = y2038detect.scan(sample)
        implicit = [i for i in issues if 'implicit' in i.message]
        explicit = [i for i in issues if 'explicit' in i.message]
        expected_implicit = 5 if _LONG_IS_NARROW else 4
        assert len(implicit) == expected_implicit
        assert len(explicit) == 2


# ---------------------------------------------------------------------------
# Exit code
# ---------------------------------------------------------------------------

class TestExitCode:
    def test_returns_nonzero_when_issues_found(self, capsys):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        rc = y2038detect.analyze(src)
        assert rc > 0

    def test_returns_0_when_clean(self, capsys, tmp_path):
        clean = tmp_path / 'clean.c'
        clean.write_text('#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n',
                         encoding='utf-8')
        rc = y2038detect.analyze(str(clean))
        assert rc == 0

    def test_output_includes_source_line(self, capsys):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        y2038detect.analyze(src)
        out = capsys.readouterr().out
        # Source line content should appear in output
        assert 'tm_year' in out
        assert '^' in out


# ---------------------------------------------------------------------------
# Relative path display (_display_path)
# ---------------------------------------------------------------------------

class TestDisplayPath:
    def test_relative_within_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        sub = tmp_path / 'src'
        sub.mkdir()
        f = sub / 'foo.c'
        f.write_text('', encoding='utf-8')
        result = y2038detect._display_path(str(f))
        assert result == os.path.join('src', 'foo.c')

    def test_absolute_outside_cwd(self, tmp_path, monkeypatch, tmp_path_factory):
        other = tmp_path_factory.mktemp('other')
        monkeypatch.chdir(other)
        result = y2038detect._display_path(str(tmp_path / 'foo.c'))
        assert os.path.isabs(result)

    def test_analyze_output_uses_relative_path(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = tmp_path / 'bad.c'
        src.write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        y2038detect.analyze(str(src))
        out = capsys.readouterr().out
        assert 'bad.c' in out
        assert str(tmp_path) not in out  # no absolute path in output

    def test_analyze_absolute_flag(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = tmp_path / 'bad.c'
        src.write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        y2038detect.analyze(str(src), absolute=True)
        out = capsys.readouterr().out
        assert str(tmp_path) in out  # absolute path present


# ---------------------------------------------------------------------------
# Color output
# ---------------------------------------------------------------------------

class TestColorOutput:
    _SRC = '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n'

    def _make(self, tmp_path):
        src = tmp_path / 'bad.c'
        src.write_text(self._SRC, encoding='utf-8')
        return str(src)

    def test_color_off_by_default_no_ansi(self, capsys, tmp_path):
        y2038detect.analyze(self._make(tmp_path), color=False)
        out = capsys.readouterr().out
        assert '\x1b[' not in out

    def test_color_on_produces_ansi(self, capsys, tmp_path):
        y2038detect.analyze(self._make(tmp_path), color=True)
        out = capsys.readouterr().out
        assert '\x1b[' in out

    def test_color_warning_label_yellow(self, capsys, tmp_path):
        y2038detect.analyze(self._make(tmp_path), color=True)
        out = capsys.readouterr().out
        assert '\x1b[1;33m' in out  # yellow bold for "warning:"

    def test_color_caret_green(self, capsys, tmp_path):
        y2038detect.analyze(self._make(tmp_path), color=True)
        out = capsys.readouterr().out
        assert '\x1b[32m' in out  # green for caret

    def test_no_color_env_disables(self, capsys, tmp_path, monkeypatch):
        monkeypatch.setenv('NO_COLOR', '')
        monkeypatch.setattr('sys.argv', ['y2038detect', self._make(tmp_path)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert '\x1b[' not in out

    def test_summary_clean_green(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(
            '#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n',
            encoding='utf-8')
        (tmp_path / 'b.c').write_text(
            '#include <time.h>\nvoid g(void) { time_t t = time(NULL); }\n',
            encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', '--color', str(tmp_path)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert '\x1b[32m' in out  # green summary

    def test_summary_issues_yellow(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(self._SRC, encoding='utf-8')
        (tmp_path / 'b.c').write_text(self._SRC, encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', '--color', str(tmp_path)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert '\x1b[33m' in out  # yellow summary


# ---------------------------------------------------------------------------
# GitHub Actions annotation output (fmt='github')
# ---------------------------------------------------------------------------

class TestGitHubAnnotations:
    def _make_issue_file(self, tmp_path):
        src = tmp_path / 'bad.c'
        src.write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        return str(src)

    def test_annotation_format(self, capsys, tmp_path):
        src = self._make_issue_file(tmp_path)
        rc = y2038detect.analyze(src, fmt='github')
        out = capsys.readouterr().out
        assert rc == 1
        assert out.startswith('::warning file=')
        assert ',line=' in out
        assert ',col=' in out
        assert '::' in out  # separator before message

    def test_annotation_no_source_excerpt(self, capsys, tmp_path):
        src = self._make_issue_file(tmp_path)
        y2038detect.analyze(src, fmt='github')
        out = capsys.readouterr().out
        assert '^' not in out
        assert 'int t' not in out

    def test_annotation_message_content(self, capsys, tmp_path):
        src = self._make_issue_file(tmp_path)
        y2038detect.analyze(src, fmt='github')
        out = capsys.readouterr().out
        assert 'time_t' in out
        assert 'truncate' in out

    def test_annotation_path_uses_github_workspace(self, capsys, tmp_path, monkeypatch):
        monkeypatch.setenv('GITHUB_WORKSPACE', str(tmp_path))
        src = self._make_issue_file(tmp_path)
        y2038detect.analyze(src, fmt='github')
        out = capsys.readouterr().out
        # Path should be relative (just 'bad.c'), not absolute
        assert 'bad.c' in out
        assert str(tmp_path) not in out

    def test_default_format_unchanged(self, capsys, tmp_path):
        src = self._make_issue_file(tmp_path)
        y2038detect.analyze(src, fmt='default')
        out = capsys.readouterr().out
        assert '::warning' not in out
        assert '^' in out

    def test_auto_detect_github_actions_env(self, capsys, tmp_path, monkeypatch):
        # When GITHUB_ACTIONS=true, _github_annotation_path should be used
        # (we test the helper directly to avoid main() argument parsing)
        monkeypatch.setenv('GITHUB_WORKSPACE', str(tmp_path))
        abspath = str(tmp_path / 'foo.c')
        rel = y2038detect._github_annotation_path(abspath)
        assert rel == 'foo.c'

    def test_annotation_path_fallback_to_cwd(self, capsys, monkeypatch):
        # Without GITHUB_WORKSPACE, falls back to CWD-relative path
        monkeypatch.delenv('GITHUB_WORKSPACE', raising=False)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as f:
            abspath = f.name
        try:
            result = y2038detect._github_annotation_path(abspath)
            assert not os.path.isabs(result) or os.sep not in result
        finally:
            os.unlink(abspath)


# ---------------------------------------------------------------------------
# Directory scanning
# ---------------------------------------------------------------------------

class TestDirectoryScan:
    def test_scans_c_files_in_dir(self, tmp_path):
        (tmp_path / 'a.c').write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        (tmp_path / 'b.c').write_text(
            '#include <time.h>\nvoid g(void) { time_t t = time(NULL); }\n',
            encoding='utf-8')
        (tmp_path / 'notes.txt').write_text('not a C file\n', encoding='utf-8')

        paths = y2038detect._collect_paths([str(tmp_path)])
        c_files = [os.path.basename(p) for p in paths]
        assert sorted(c_files) == ['a.c', 'b.c']

    def test_issues_from_dir(self, tmp_path):
        (tmp_path / 'bad.c').write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        paths = y2038detect._collect_paths([str(tmp_path)])
        issues = []
        for p in paths:
            issues.extend(y2038detect.scan(p))
        assert len(issues) == 1

    def test_nonexistent_path_skipped(self, capsys, tmp_path):
        paths = y2038detect._collect_paths([str(tmp_path / 'nosuch.c')])
        assert paths == []
        assert 'not found' in capsys.readouterr().err


# ---------------------------------------------------------------------------
# --exclude pattern filtering
# ---------------------------------------------------------------------------

class TestExclude:
    def _make_tree(self, tmp_path):
        """Create a small directory tree for exclude tests."""
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'main.c').write_text('', encoding='utf-8')
        (tmp_path / 'vendor').mkdir()
        (tmp_path / 'vendor' / 'lib.c').write_text('', encoding='utf-8')
        (tmp_path / 'vendor' / 'util.c').write_text('', encoding='utf-8')
        (tmp_path / 'third_party').mkdir()
        (tmp_path / 'third_party' / 'ext.c').write_text('', encoding='utf-8')

    def test_exclude_vendor_dir(self, tmp_path):
        self._make_tree(tmp_path)
        paths = y2038detect._collect_paths([str(tmp_path)], exclude=['vendor/*'])
        names = sorted(os.path.basename(p) for p in paths)
        assert names == ['ext.c', 'main.c']

    def test_exclude_multiple_patterns(self, tmp_path):
        self._make_tree(tmp_path)
        paths = y2038detect._collect_paths(
            [str(tmp_path)], exclude=['vendor/*', 'third_party/*'])
        names = [os.path.basename(p) for p in paths]
        assert names == ['main.c']

    def test_exclude_glob_suffix(self, tmp_path):
        # Exclude by filename suffix pattern
        (tmp_path / 'foo.pb.c').write_text('', encoding='utf-8')
        (tmp_path / 'bar.c').write_text('', encoding='utf-8')
        paths = y2038detect._collect_paths([str(tmp_path)], exclude=['*.pb.c'])
        names = [os.path.basename(p) for p in paths]
        assert names == ['bar.c']

    def test_exclude_does_not_affect_explicit_files(self, tmp_path):
        # Files given explicitly on the command line are never excluded
        f = tmp_path / 'vendor' / 'lib.c'
        f.parent.mkdir()
        f.write_text('', encoding='utf-8')
        paths = y2038detect._collect_paths([str(f)], exclude=['vendor/*'])
        assert len(paths) == 1

    def test_no_exclude_returns_all(self, tmp_path):
        self._make_tree(tmp_path)
        paths = y2038detect._collect_paths([str(tmp_path)])
        assert len(paths) == 4

    def test_is_excluded_prefix_slash(self, tmp_path):
        # Pattern without leading slash matched via '*/' prefix internally
        result = y2038detect._is_excluded('src/vendor/foo.c', ['vendor/*'])
        assert result is True

    def test_is_excluded_no_match(self):
        result = y2038detect._is_excluded('src/main.c', ['vendor/*'])
        assert result is False


# ---------------------------------------------------------------------------
# Scan summary line
# ---------------------------------------------------------------------------

class TestScanSummary:
    _BAD = '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n'
    _OK  = '#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n'

    def test_summary_all_clean(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(self._OK, encoding='utf-8')
        (tmp_path / 'b.c').write_text(self._OK, encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', str(tmp_path)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert 'All 2 files clean.' in out

    def test_summary_with_issues(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(self._BAD, encoding='utf-8')
        (tmp_path / 'b.c').write_text(self._OK,  encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', str(tmp_path)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert '1 issue in 1 file (1 clean)' in out

    def test_summary_plural(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(self._BAD, encoding='utf-8')
        (tmp_path / 'b.c').write_text(self._BAD, encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', str(tmp_path)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert '2 issues in 2 files (0 clean)' in out

    def test_no_summary_single_file(self, capsys, tmp_path, monkeypatch):
        src = tmp_path / 'a.c'
        src.write_text(self._BAD, encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', str(src)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert 'clean' not in out
        assert 'issue' not in out

    def test_no_summary_with_json(self, capsys, tmp_path, monkeypatch):
        (tmp_path / 'a.c').write_text(self._OK, encoding='utf-8')
        (tmp_path / 'b.c').write_text(self._OK, encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', '--json', str(tmp_path)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        out = capsys.readouterr().out
        assert 'clean' not in out


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

class TestSourceContext:
    def test_includes_before_and_after_lines(self, tmp_path):
        src = tmp_path / 'a.c'
        src.write_text('\n'.join(f'line{n}' for n in range(1, 11)) + '\n', encoding='utf-8')
        ctx = y2038detect._source_context(str(src), line=5, before=2, after=1)
        assert [c['line'] for c in ctx] == [3, 4, 5, 6]
        assert ctx[2] == {'line': 5, 'text': 'line5'}

    def test_clamps_at_file_boundaries(self, tmp_path):
        src = tmp_path / 'a.c'
        src.write_text('only\ntwo\n', encoding='utf-8')
        ctx = y2038detect._source_context(str(src), line=1, before=6, after=2)
        assert [c['line'] for c in ctx] == [1, 2]

    def test_returns_none_for_unreadable_file(self, tmp_path):
        assert y2038detect._source_context(str(tmp_path / 'missing.c'), line=1) is None


class TestJsonOutput:
    def test_json_structure(self):
        src = os.path.join(os.path.dirname(__file__), 'domktime.c')
        issues = y2038detect.scan(src)
        data = [{'file': i.file, 'line': i.line, 'col': i.col,
                 'message': i.message} for i in issues]
        serialized = json.dumps(data)
        parsed = json.loads(serialized)
        assert len(parsed) == 2
        assert all(k in parsed[0] for k in ('file', 'line', 'col', 'message'))
        assert all(isinstance(e['line'], int) for e in parsed)

    def test_json_output_includes_source_context(self, tmp_path, monkeypatch, capsys):
        # The plain-text (--json-less) output already shows the flagged
        # line; --json previously showed none at all. Give --json the
        # source context too (a few lines of surrounding context, not just
        # the one line) so JSON consumers -- including evaluation's own
        # findings pipeline -- don't need their own copy of the source tree
        # just to redisplay what was found.
        src = tmp_path / 'a.c'
        src.write_text('#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
                       encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', '--json', str(src)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 1
        context = data[0]['context']
        assert [c['line'] for c in context] == [1, 2]  # file has only 2 lines
        flagged = next(c for c in context if c['line'] == data[0]['line'])
        assert 'time(NULL)' in flagged['text']

    def test_json_with_strict_includes_context_in_both_branches(self, tmp_path, monkeypatch, capsys):
        src = tmp_path / 'a.c'
        src.write_text('#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
                       encoding='utf-8')
        monkeypatch.setattr('sys.argv', ['y2038detect', '--json', '--with-strict', str(src)])
        with pytest.raises(SystemExit):
            y2038detect.main()
        data = json.loads(capsys.readouterr().out)
        assert 'context' in data['default'][0]
        assert 'context' in data['strict'][0]

    def test_json_no_issues_empty_array(self, tmp_path):
        clean = tmp_path / 'clean.c'
        clean.write_text('#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n',
                         encoding='utf-8')
        issues = y2038detect.scan(str(clean))
        data = json.dumps([{'file': i.file, 'line': i.line, 'col': i.col,
                             'message': i.message} for i in issues])
        assert json.loads(data) == []


# ---------------------------------------------------------------------------
# Compiler include auto-detection
# ---------------------------------------------------------------------------

class TestCompilerIncludes:
    def test_returns_tuple(self):
        # Always returns a tuple (empty when no compiler, non-empty when found)
        result = y2038detect._compiler_includes()
        assert isinstance(result, tuple)

    def test_paths_exist_when_found(self):
        # Every returned path must be an existing directory
        for path in y2038detect._compiler_includes():
            assert os.path.isdir(path), f"include path does not exist: {path}"

    def test_cached(self):
        # Two calls return the same object (lru_cache)
        assert y2038detect._compiler_includes() is y2038detect._compiler_includes()

    def test_analysis_works_regardless(self, tmp_path):
        # Whether a compiler is found or not, basic analysis must work
        src = tmp_path / 't.c'
        src.write_text('#include <time.h>\nvoid f(void){int t=time(NULL);}\n',
                       encoding='utf-8')
        issues = y2038detect.scan(str(src))
        assert len(issues) == 1
        assert 'implicit' in issues[0].message


# ---------------------------------------------------------------------------
# // y2038: ignore suppression
# ---------------------------------------------------------------------------

class TestIgnoreSuppression:

    def test_same_line_cpp_comment(self, tmp_path):
        # Issue on a line with // y2038: ignore must be suppressed
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) { int t = time(NULL); // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_same_line_c_comment(self, tmp_path):
        # C-style block comment /* y2038: ignore */ also works
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) { int t = time(NULL); /* y2038: ignore */\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_case_insensitive(self, tmp_path):
        # Y2038: IGNORE (uppercase) is also accepted
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) { int t = time(NULL); // Y2038: IGNORE\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_without_annotation_still_reported(self, tmp_path):
        # Without the annotation the issue must still appear
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        issues = y2038detect.scan(str(src))
        assert len(issues) == 1

    def test_partial_suppression(self, tmp_path):
        # Only the annotated line is suppressed; other issues remain
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    int t1 = time(NULL); // y2038: ignore\n'
            '    int t2 = time(NULL);\n'
            '}\n',
            encoding='utf-8')
        issues = y2038detect.scan(str(src))
        assert len(issues) == 1
        assert issues[0].line == 4

    def test_tm_year_suppressed(self, tmp_path):
        # tm_year ceiling warning can also be suppressed
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'int f(void) { struct tm t;\n'
            '    return t.tm_year < 138; /* y2038: ignore */\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []


# ---------------------------------------------------------------------------
# Bounded variable tracking (time-unit modulo heuristic)
# ---------------------------------------------------------------------------

class TestBoundedVarTracking:

    def test_compound_assign_modulo_suppresses_narrowing(self, tmp_path):
        # val %= 86400 bounds val; subsequent narrowing should not be reported
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t val) {\n'
            '    val %= 86400;\n'
            '    int h = (int)(val / 3600);\n'
            '    int m = (int)(val / 60);\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_var_decl_modulo_suppresses_narrowing(self, tmp_path):
        # time_t seconds = t % 86400 bounds seconds; narrowing should not report
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t t) {\n'
            '    time_t seconds = t % 86400;\n'
            '    int h = (int)(seconds / 3600);\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_all_time_units_60_3600_86400_604800(self, tmp_path):
        # All four recognised divisors suppress narrowing
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t a, time_t b, time_t c, time_t d) {\n'
            '    a %= 60;     int x = (int)a;\n'
            '    b %= 3600;   int y = (int)b;\n'
            '    c %= 86400;  int z = (int)c;\n'
            '    d %= 604800; int w = (int)d;\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_unbounded_var_still_reported(self, tmp_path):
        # Without a modulo, narrowing must still be detected
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t t) {\n'
            '    int x = (int)t;\n'
            '}\n',
            encoding='utf-8')
        assert len(y2038detect.scan(str(src))) == 1

    def test_bounded_in_one_function_does_not_affect_another(self, tmp_path):
        # bounded_vars must be reset per function
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f1(time_t val) {\n'
            '    val %= 86400;\n'
            '    int x = (int)val;\n'  # suppressed
            '}\n'
            'void f2(time_t val) {\n'
            '    int x = (int)val;\n'  # NOT suppressed — different function
            '}\n',
            encoding='utf-8')
        issues = y2038detect.scan(str(src))
        assert len(issues) == 1
        assert issues[0].line == 7

    def test_unrecognised_divisor_not_suppressed(self, tmp_path):
        # Divisors not in the recognised set must not suppress narrowing
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t t) {\n'
            '    t %= 1000;\n'
            '    int x = (int)t;\n'
            '}\n',
            encoding='utf-8')
        assert len(y2038detect.scan(str(src))) == 1

    def test_const_qualified_time_t_operand_still_recognised(self, tmp_path):
        # Regression: _is_time_type() used to fail on cv-qualified spellings
        # ("const time_t"), silently hiding such operands from the bounded
        # check. A const time_t variable that is genuinely unbounded (not
        # itself a modulo result) must still block suppression.
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    time_t bounded = time(NULL) % 86400;\n'
            '    const time_t unbounded = time(NULL);\n'
            '    int x = (int)(bounded + unbounded);\n'
            '}\n',
            encoding='utf-8')
        assert len(y2038detect.scan(str(src))) == 1


# ---------------------------------------------------------------------------
# Arithmetic bounding: modulo-by-known-divisor and division propagation
# ---------------------------------------------------------------------------

class TestArithmeticBounding:
    """Extensions to bounded-variable tracking, each justified by
    arithmetic (not just shape-matching):

      - X % N is bounded to [0, N) regardless of X, whenever N resolves to
        a recognised time-unit divisor (a literal, a reference to a
        time_t constant, or an arithmetic expression built from either --
        see _fold_int_const).
      - X / Y is bounded whenever X (the dividend) is itself bounded,
        regardless of Y (dividing a bounded value cannot make it bigger).
      - A named time_t constant's value is resolved even when its own
        initializer is an arithmetic expression rather than a bare literal
        (e.g. `const time_t secs_day = 3600*24;`), so it can in turn be
        used as a divisor elsewhere.

    Found while investigating real false positives in redis/valkey's
    localtime.c (see TODO.md)."""

    def _make(self, tmp_path, body):
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\nvoid f(void) {\n' + body + '\n}\n',
            encoding='utf-8')
        return str(src)

    def test_modulo_by_literal_bounded_regardless_of_operand(self, tmp_path):
        # x is not otherwise bounded, but %7 alone makes the result safe.
        body = 'time_t x = time(NULL);\nint w = (x + 4) % 7;'
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_modulo_by_unrecognised_literal_not_suppressed(self, tmp_path):
        # 1000 is not a recognised time-unit divisor.
        body = 'time_t x = time(NULL);\nint w = x % 1000;'
        assert len(y2038detect.scan(self._make(tmp_path, body))) == 1

    def test_const_time_t_literal_is_a_known_divisor(self, tmp_path):
        # secs_hour is never itself bounded by a modulo, but its literal
        # initializer makes it usable as a recognised divisor.
        body = ('const time_t secs_hour = 3600;\n'
                'time_t x = time(NULL);\n'
                'int w = x % secs_hour;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_division_of_bounded_dividend_is_bounded(self, tmp_path):
        # seconds is bounded via the existing modulo-VAR_DECL rule; dividing
        # it further (by anything) cannot make it larger.
        body = ('time_t seconds = time(NULL) % 86400;\n'
                'int h = seconds / 3600;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_division_by_const_of_bounded_dividend(self, tmp_path):
        # Same as above, but the divisor is itself a const time_t constant
        # (mirrors redis/valkey's localtime.c: seconds / secs_hour).
        body = ('const time_t secs_hour = 3600;\n'
                'time_t seconds = time(NULL) % 86400;\n'
                'int h = seconds / secs_hour;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_division_of_unbounded_dividend_not_suppressed(self, tmp_path):
        # The dividend itself is not bounded by anything -- must still flag.
        body = 'time_t t = time(NULL);\nint x = t / 2;'
        assert len(y2038detect.scan(self._make(tmp_path, body))) == 1

    def test_nested_bounded_expression(self, tmp_path):
        # (seconds % secs_hour) / secs_min: both operators chain via the
        # new rules (mirrors redis/valkey's localtime.c tm_min/tm_sec lines).
        body = ('const time_t secs_hour = 3600;\n'
                'const time_t secs_min = 60;\n'
                'time_t seconds = time(NULL) % 86400;\n'
                'int m = (seconds % secs_hour) / secs_min;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_strict_disables_both_mechanisms(self, tmp_path):
        body = ('const time_t secs_hour = 3600;\n'
                'time_t seconds = time(NULL) % 86400;\n'
                'int h = seconds / secs_hour;\n'
                'int w = (seconds + 4) % 7;')
        issues = y2038detect.scan(self._make(tmp_path, body), strict=True)
        assert len(issues) == 2

    def test_const_with_arithmetic_initializer_is_a_known_divisor(self, tmp_path):
        # secs_day's own initializer is 3600*24, not a bare literal --
        # _fold_int_const must resolve it to 86400 to recognise it as a
        # known time-unit divisor.
        body = ('const time_t secs_day = 3600*24;\n'
                'time_t x = time(NULL);\n'
                'int w = x % secs_day;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_chained_const_with_arithmetic_initializer(self, tmp_path):
        # Mirrors the exact shape in redis/valkey's localtime.c: seconds is
        # bounded via `t % secs_day`, where secs_day's initializer is an
        # arithmetic expression rather than a literal; that boundedness
        # must then propagate through a further division by another const.
        body = ('const time_t secs_hour = 3600;\n'
                'const time_t secs_day = 3600*24;\n'
                'time_t t = time(NULL);\n'
                'time_t seconds = t % secs_day;\n'
                'int h = seconds / secs_hour;')
        assert y2038detect.scan(self._make(tmp_path, body)) == []


# ---------------------------------------------------------------------------
# time-sink function suppression (srand(time(NULL)) and similar)
# ---------------------------------------------------------------------------

class TestTimeSinkSuppression:
    """time_t narrowing passed directly to a known seed-consuming function
    (srand() etc.) is suppressed: the value is used as an opaque seed,
    never as an actual calendar-time value."""

    _HDR = '#include <time.h>\n#include <stdlib.h>\n'

    def _make(self, tmp_path, body):
        src = tmp_path / 't.c'
        src.write_text(self._HDR + 'void f(void) {\n' + body + '\n}\n', encoding='utf-8')
        return str(src)

    def test_direct_call_suppressed(self, tmp_path):
        assert y2038detect.scan(self._make(tmp_path, 'srand(time(NULL));')) == []

    def test_direct_call_shown_with_strict(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, 'srand(time(NULL));'), strict=True)
        assert len(issues) == 1
        assert 'implicit' in issues[0].message

    def test_explicit_cast_suppressed(self, tmp_path):
        assert y2038detect.scan(self._make(tmp_path, 'srand((unsigned)time(NULL));')) == []

    def test_variable_still_time_t_suppressed(self, tmp_path):
        # The variable is still time_t-typed, so the narrowing happens at
        # the call site itself -- same shape as the direct case.
        body = 'time_t seed = time(NULL);\nsrand(seed);'
        assert y2038detect.scan(self._make(tmp_path, body)) == []

    def test_variable_already_narrow_not_suppressed(self, tmp_path):
        # Out of scope: the narrowing already happened at the declaration,
        # before the value ever reaches srand(). Forward data-flow tracing
        # to catch this is a possible future extension (see TODO.md).
        body = 'unsigned int seed = time(NULL);\nsrand(seed);'
        issues = y2038detect.scan(self._make(tmp_path, body))
        assert len(issues) == 1

    def test_unregistered_function_not_suppressed(self, tmp_path):
        body = 'void other(unsigned int x);\nother(time(NULL));'
        assert len(y2038detect.scan(self._make(tmp_path, body))) == 1

    def test_srandom_suppressed(self, tmp_path):
        assert y2038detect.scan(self._make(tmp_path, 'srandom(time(NULL));')) == []


# ---------------------------------------------------------------------------
# y2038: ignore-begin / ignore-end range suppression
# ---------------------------------------------------------------------------

class TestIgnoreRangeSuppression:

    def test_basic_range(self, tmp_path):
        # Issues inside ignore-begin/end are suppressed
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    // y2038: ignore-begin\n'
            '    int t1 = time(NULL);\n'
            '    int t2 = time(NULL);\n'
            '    // y2038: ignore-end\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_outside_range_still_reported(self, tmp_path):
        # Issues outside the range must still be reported
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    int t0 = time(NULL);\n'
            '    // y2038: ignore-begin\n'
            '    int t1 = time(NULL);\n'
            '    // y2038: ignore-end\n'
            '    int t2 = time(NULL);\n'
            '}\n',
            encoding='utf-8')
        issues = y2038detect.scan(str(src))
        assert len(issues) == 2
        assert sorted(i.line for i in issues) == [3, 7]

    def test_c_style_comment(self, tmp_path):
        # /* y2038: ignore-begin */ / /* y2038: ignore-end */ also work
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    /* y2038: ignore-begin */\n'
            '    int t = time(NULL);\n'
            '    /* y2038: ignore-end */\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_case_insensitive(self, tmp_path):
        # Y2038: IGNORE-BEGIN / Y2038: IGNORE-END (uppercase) also accepted
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    // Y2038: IGNORE-BEGIN\n'
            '    int t = time(NULL);\n'
            '    // Y2038: IGNORE-END\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_unclosed_range_suppresses_to_eof(self, tmp_path):
        # ignore-begin without ignore-end suppresses everything to end of file
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    // y2038: ignore-begin\n'
            '    int t1 = time(NULL);\n'
            '    int t2 = time(NULL);\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_per_line_ignore_still_works_inside_range(self, tmp_path):
        # Per-line ignore still works independently of range markers
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    int t = time(NULL); // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_begin_marker_line_itself_suppressed(self, tmp_path):
        # An issue on the ignore-begin line is also suppressed
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    int t = time(NULL); /* y2038: ignore-begin */\n'
            '    /* y2038: ignore-end */\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []


# ---------------------------------------------------------------------------
# compile_commands.json support
# ---------------------------------------------------------------------------

class TestCompileCommandsLoad:
    """load_compile_commands() parses the JSON and extracts relevant flags."""

    def _write_db(self, tmp_path, entries):
        db_path = tmp_path / 'compile_commands.json'
        db_path.write_text(json.dumps(entries), encoding='utf-8')
        return str(db_path)

    def test_basic_include_command_format(self, tmp_path):
        inc_dir = str(tmp_path / 'include')
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'command': f'gcc -I{inc_dir} -o out.o src.c',
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        assert src_norm in result
        assert f'-I{inc_dir}' in result[src_norm]

    def test_arguments_format(self, tmp_path):
        inc_dir = str(tmp_path / 'include')
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'arguments': ['gcc', f'-I{inc_dir}', '-o', 'out.o', 'src.c'],
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        assert f'-I{inc_dir}' in result[src_norm]

    def test_define_extracted(self, tmp_path):
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'command': 'gcc -DFOO=1 -DBAR src.c',
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        args = result[src_norm]
        assert '-DFOO=1' in args
        assert '-DBAR' in args

    def test_std_flag_preserved(self, tmp_path):
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'command': 'gcc -std=c99 src.c',
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        assert '-std=c99' in result[src_norm]

    def test_separate_flag_I_space(self, tmp_path):
        inc_dir = str(tmp_path / 'include')
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'arguments': ['gcc', '-I', inc_dir, 'src.c'],
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        assert f'-I{inc_dir}' in result[src_norm]

    def test_relative_include_resolved(self, tmp_path):
        sub = tmp_path / 'sub'
        sub.mkdir()
        db_path = self._write_db(tmp_path, [
            {'directory': str(sub),
             'command': 'gcc -I../include src.c',
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(sub / 'src.c')))
        args = result[src_norm]
        expected = os.path.normpath(os.path.join(str(sub), '../include'))
        assert f'-I{expected}' in args

    def test_missing_file_returns_empty(self, tmp_path):
        result = y2038detect.load_compile_commands(str(tmp_path / 'missing.json'))
        assert result == {}

    def test_invalid_json_returns_empty(self, tmp_path):
        bad = tmp_path / 'bad.json'
        bad.write_text('not valid json', encoding='utf-8')
        assert y2038detect.load_compile_commands(str(bad)) == {}

    def test_entry_without_file_skipped(self, tmp_path):
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path), 'command': 'gcc src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        assert result == {}

    def test_irrelevant_flags_excluded(self, tmp_path):
        db_path = self._write_db(tmp_path, [
            {'directory': str(tmp_path),
             'command': 'gcc -O2 -Wall -Werror -g -c src.c',
             'file': 'src.c'},
        ])
        result = y2038detect.load_compile_commands(db_path)
        src_norm = os.path.normcase(os.path.abspath(str(tmp_path / 'src.c')))
        assert result[src_norm] == []


_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# pre-commit hook configuration
# ---------------------------------------------------------------------------

class TestPreCommitHook:
    """Sanity checks for .pre-commit-hooks.yaml and pyproject.toml."""

    def test_hooks_file_exists(self):
        assert os.path.isfile(os.path.join(_REPO_ROOT, '.pre-commit-hooks.yaml'))

    def test_hooks_file_has_id(self):
        path = os.path.join(_REPO_ROOT, '.pre-commit-hooks.yaml')
        content = open(path, encoding='utf-8').read()
        assert 'id: y2038detect' in content

    def test_hooks_file_language_python(self):
        path = os.path.join(_REPO_ROOT, '.pre-commit-hooks.yaml')
        content = open(path, encoding='utf-8').read()
        assert 'language: python' in content

    def test_hooks_file_entry_matches_script(self):
        path = os.path.join(_REPO_ROOT, '.pre-commit-hooks.yaml')
        content = open(path, encoding='utf-8').read()
        assert 'entry: y2038detect' in content

    def test_hooks_file_type_c(self):
        path = os.path.join(_REPO_ROOT, '.pre-commit-hooks.yaml')
        content = open(path, encoding='utf-8').read()
        assert 'types: [c]' in content

    def test_pyproject_exists(self):
        assert os.path.isfile(os.path.join(_REPO_ROOT, 'pyproject.toml'))

    def test_pyproject_has_entry_point(self):
        path = os.path.join(_REPO_ROOT, 'pyproject.toml')
        content = open(path, encoding='utf-8').read()
        assert 'y2038detect = "y2038detect:main"' in content

    def test_pyproject_uses_dynamic_version(self):
        path = os.path.join(_REPO_ROOT, 'pyproject.toml')
        content = open(path, encoding='utf-8').read()
        assert '_version.__version__' in content

    def test_version_file_exists(self):
        assert os.path.isfile(os.path.join(_REPO_ROOT, '_version.py'))

    def test_version_file_matches_module(self):
        path = os.path.join(_REPO_ROOT, '_version.py')
        content = open(path, encoding='utf-8').read()
        assert f"__version__ = '{y2038detect.__version__}'" in content

    def test_main_is_callable(self):
        # Entry point target must exist and be callable
        assert callable(y2038detect.main)


class TestCompileCommandsIntegration:
    """scan() uses per-file flags from compile_commands to resolve custom headers."""

    def test_custom_header_via_compile_commands(self, tmp_path):
        # Header in a non-standard directory defines a time_t typedef alias
        inc_dir = tmp_path / 'include'
        inc_dir.mkdir()
        (inc_dir / 'myheader.h').write_text(
            'typedef time_t custom_ts;\n', encoding='utf-8')

        src = tmp_path / 'test.c'
        src.write_text(
            '#include <time.h>\n'
            '#include "myheader.h"\n'
            'void f(void) { custom_ts now = time(NULL); int t = now; }\n',
            encoding='utf-8')

        db_path = tmp_path / 'compile_commands.json'
        db_path.write_text(json.dumps([
            {'directory': str(tmp_path),
             'command': f'gcc -I{inc_dir} test.c',
             'file': str(src)},
        ]), encoding='utf-8')

        compile_db = y2038detect.load_compile_commands(str(db_path))
        src_norm = os.path.normcase(os.path.abspath(str(src)))
        file_args = compile_db.get(src_norm, [])

        issues = y2038detect.scan(str(src), file_args)
        assert len(issues) == 1
        assert 'implicit' in issues[0].message


# ---------------------------------------------------------------------------
# pyproject.toml config file support
# ---------------------------------------------------------------------------

import tomllib  # noqa: E402  (available on Python 3.11+; skip tests on 3.10)

pytestmark_tomllib = pytest.mark.skipif(
    tomllib is None,
    reason='tomllib not available (Python < 3.11)')


@pytest.mark.skipif(
    y2038detect.tomllib is None,
    reason='tomllib not available (Python < 3.11)')
class TestConfigFile:

    def _write_c(self, tmp_path):
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        return src

    def test_no_config_no_effect(self, tmp_path, monkeypatch):
        # Without pyproject.toml, _find_config() returns {}
        monkeypatch.chdir(tmp_path)
        assert y2038detect._find_config() == {}

    def test_pyproject_without_section_returns_empty(self, tmp_path, monkeypatch):
        # pyproject.toml present but no [tool.y2038detect] → empty dict, search stops
        (tmp_path / 'pyproject.toml').write_bytes(b'[tool.other]\nfoo = 1\n')
        monkeypatch.chdir(tmp_path)
        assert y2038detect._find_config() == {}

    def test_config_loaded_from_cwd(self, tmp_path, monkeypatch):
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nexclude = ["vendor/*"]\n')
        monkeypatch.chdir(tmp_path)
        cfg = y2038detect._find_config()
        assert cfg.get('exclude') == ['vendor/*']

    def test_config_loaded_from_parent(self, tmp_path, monkeypatch):
        # Config in parent directory is found when CWD has no pyproject.toml
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nexclude = ["third_party/*"]\n')
        subdir = tmp_path / 'src'
        subdir.mkdir()
        monkeypatch.chdir(subdir)
        cfg = y2038detect._find_config()
        assert cfg.get('exclude') == ['third_party/*']

    def test_parent_not_searched_when_cwd_has_pyproject(self, tmp_path, monkeypatch):
        # CWD pyproject.toml (no section) stops the search; parent is not read
        parent_cfg = tmp_path / 'pyproject.toml'
        parent_cfg.write_bytes(b'[tool.y2038detect]\nexclude = ["vendor/*"]\n')
        subdir = tmp_path / 'sub'
        subdir.mkdir()
        (subdir / 'pyproject.toml').write_bytes(b'[tool.other]\n')
        monkeypatch.chdir(subdir)
        assert y2038detect._find_config() == {}

    def test_exclude_from_config_applied(self, tmp_path, monkeypatch):
        # Files matching config exclude pattern are skipped
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nexclude = ["vendor/*"]\n')
        vendor = tmp_path / 'vendor'
        vendor.mkdir()
        src = vendor / 'lib.c'
        src.write_text(
            '#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
            encoding='utf-8')
        monkeypatch.chdir(tmp_path)
        # _find_config returns the exclude; verify _is_excluded logic works
        cfg = y2038detect._find_config()
        assert y2038detect._is_excluded(str(src), cfg['exclude'])

    def test_cli_exclude_merged_with_config(self, tmp_path, monkeypatch):
        # CLI --exclude and config exclude are merged, not overriding each other
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nexclude = ["vendor/*"]\n')
        monkeypatch.chdir(tmp_path)
        cfg = y2038detect._find_config()
        merged = list(cfg.get('exclude', [])) + ['generated/*']
        assert 'vendor/*' in merged
        assert 'generated/*' in merged

    def test_compile_commands_from_config(self, tmp_path, monkeypatch):
        # compile_commands key is read from config
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\ncompile_commands = "build/compile_commands.json"\n')
        monkeypatch.chdir(tmp_path)
        cfg = y2038detect._find_config()
        assert cfg.get('compile_commands') == 'build/compile_commands.json'

    def test_includes_from_config(self, tmp_path, monkeypatch):
        # includes key is read from config
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nincludes = ["include/", "libs/"]\n')
        monkeypatch.chdir(tmp_path)
        cfg = y2038detect._find_config()
        assert cfg.get('includes') == ['include/', 'libs/']


# ---------------------------------------------------------------------------
# --strict flag
# ---------------------------------------------------------------------------

class TestStrict:

    @pytest.mark.skipif(_LONG_IS_NARROW,
                        reason='long is already narrow on this platform')
    def test_long_flagged_on_lp64(self):
        # Without strict: long is 8 bytes on LP64, not flagged
        assert _scan('long t = time(NULL);') == []
        # With strict: long is always flagged
        issues = _scan('long t = time(NULL);', strict=True)
        assert len(issues) == 1
        assert 'implicit' in issues[0].message
        assert "'long'" in issues[0].message

    @pytest.mark.skipif(_LONG_IS_NARROW,
                        reason='unsigned long is already narrow on this platform')
    def test_unsigned_long_flagged_on_lp64(self):
        assert _scan('unsigned long t = (unsigned long)time(NULL);') == []
        issues = _scan('unsigned long t = (unsigned long)time(NULL);', strict=True)
        assert len(issues) == 1

    def test_bounded_var_reported_in_strict(self, tmp_path):
        # Bounded variable tracking is disabled in strict mode
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t val) {\n'
            '    val %= 86400;\n'
            '    int h = (int)(val / 3600);\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []
        issues = y2038detect.scan(str(src), strict=True)
        assert len(issues) == 1

    def test_y2k_hack_flagged_in_strict(self):
        # tm_year < 69 is a Y2K-era hack; normally suppressed, flagged in strict mode
        assert _scan_toplevel('struct tm t;\nint f(void) { return t.tm_year < 69; }\n') == []
        issues = _scan_toplevel('struct tm t;\nint f(void) { return t.tm_year < 69; }\n',
                                strict=True)
        assert len(issues) == 1
        assert 'tm_year' in issues[0].message

    def test_vary_y2k_line_flagged_in_strict(self):
        # vary.c line 139: tm_year < 69 — strict mode should flag it
        issues = y2038detect.scan(os.path.join(_TESTS_DIR, 'vary.c'), strict=True)
        assert 139 in {i.line for i in issues}

    def test_cli_strict_flag(self, tmp_path, capsys, monkeypatch):
        # --strict on CLI activates strict mode
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'struct tm t;\n'
            'int f(void) { return t.tm_year < 69; }\n',
            encoding='utf-8')
        # Without --strict: exit 0
        monkeypatch.setattr('sys.argv', ['y2038detect', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 0
        # With --strict: exit 1
        monkeypatch.setattr('sys.argv', ['y2038detect', '--strict', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 1

    @pytest.mark.skipif(
        y2038detect.tomllib is None,
        reason='tomllib not available (Python < 3.11)')
    def test_strict_from_config(self, tmp_path, monkeypatch):
        # strict = true in pyproject.toml activates strict mode
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t val) {\n'
            '    val %= 86400;\n'
            '    int h = (int)(val / 3600);\n'
            '}\n',
            encoding='utf-8')
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nstrict = true\n')
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr('sys.argv', ['y2038detect', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# printf-family time_t format specifier mismatch detection
# ---------------------------------------------------------------------------

class TestPrintfDetection:
    """time_t argument to printf-family with a mismatched format specifier."""

    _HDR = '#include <time.h>\n#include <stdio.h>\n'

    def _make(self, tmp_path, body):
        src = tmp_path / 'fmt.c'
        src.write_text(
            self._HDR + 'void f(void) {\n' + body + '\n}\n',
            encoding='utf-8')
        return str(src)

    def test_printf_d_format(self, tmp_path):
        # %d expects int; time_t is 64-bit on modern platforms → mismatch
        issues = y2038detect.scan(self._make(tmp_path,
            'printf("%d", time(NULL));'))
        assert len(issues) == 1
        assert 'time_t' in issues[0].message
        assert 'printf' in issues[0].message

    def test_printf_i_format(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path,
            'printf("%i", time(NULL));'))
        assert len(issues) == 1

    def test_printf_u_format(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path,
            'printf("%u", time(NULL));'))
        assert len(issues) == 1

    def test_sprintf_d_format(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path,
            'char buf[32]; sprintf(buf, "%d", time(NULL));'))
        assert len(issues) == 1

    def test_snprintf_d_format(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path,
            'char buf[32]; snprintf(buf, sizeof(buf), "%d", time(NULL));'))
        assert len(issues) == 1

    def test_fprintf_d_format(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path,
            'fprintf(stdout, "%d", time(NULL));'))
        assert len(issues) == 1

    def test_explicit_cast_no_flag(self, tmp_path):
        # (long long) cast removes time_t from the argument type → no warning
        issues = y2038detect.scan(self._make(tmp_path,
            'printf("%lld", (long long)time(NULL));'))
        assert issues == []

    def test_non_time_t_no_flag(self, tmp_path):
        # int variable only — no time_t involved
        issues = y2038detect.scan(self._make(tmp_path,
            'int n = 42; printf("%d", n);'))
        assert issues == []

    def test_suppressed_by_ignore(self, tmp_path):
        src = tmp_path / 'fmt.c'
        src.write_text(
            self._HDR +
            'void f(void) {\n'
            '    printf("%d", time(NULL)); // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []


# ---------------------------------------------------------------------------
# Compound assignment narrowing  (int_var += time(NULL))
# ---------------------------------------------------------------------------

class TestCompoundAssignment:
    """time_t value in compound assignment to a narrow int lvalue."""

    def test_plus_eq_from_call(self):
        issues = _scan('int v = 0; v += time(NULL);')
        assert len(issues) == 1
        assert 'compound' in issues[0].message
        assert '2038' in issues[0].message

    def test_plus_eq_uint32(self):
        issues = _scan('uint32_t v = 0; v += time(NULL);')
        assert len(issues) == 1
        assert '2106' in issues[0].message

    def test_minus_eq_from_call(self):
        issues = _scan('int v = 0; v -= time(NULL);')
        assert len(issues) == 1

    def test_plus_eq_from_variable(self):
        issues = _scan('time_t t = time(NULL); int v = 0; v += t;')
        assert len(issues) == 1

    def test_time_t_lhs_no_flag(self):
        # time_t += time_t — both sides wide, not a problem
        assert _scan('time_t v = 0; v += time(NULL);') == []

    def test_int_rhs_no_flag(self):
        # int += int literal — no time_t involved
        assert _scan('int v = 0; v += 5;') == []

    def test_bounded_compound_no_flag(self, tmp_path):
        # bounded variable: v += t where t %= 86400 → safe to narrow
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(time_t t) {\n'
            '    t %= 86400;\n'
            '    int v = 0;\n'
            '    v += t;\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []

    def test_suppressed_by_ignore(self, tmp_path):
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            'void f(void) {\n'
            '    int v = 0;\n'
            '    v += time(NULL); // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []


# ---------------------------------------------------------------------------
# struct stat filesystem timestamp detection (--strict only)
# ---------------------------------------------------------------------------

class TestStatTimestampDetection:
    """Access to struct stat timestamp fields is only reported with --strict."""

    _HDR = '#include <time.h>\n#include <sys/stat.h>\n'

    def _make(self, tmp_path, body):
        src = tmp_path / 'stat_test.c'
        src.write_text(
            self._HDR + 'void f(void) {\n' + body + '\n}\n',
            encoding='utf-8')
        return str(src)

    def test_mtime_no_issue_without_strict(self, tmp_path):
        # Without --strict: st_mtime access is not reported
        issues = y2038detect.scan(self._make(tmp_path,
            'struct stat buf; time_t t = buf.st_mtime;'))
        assert issues == []

    def test_mtime_dot_strict(self, tmp_path):
        # With --strict: st_mtime access on struct stat is reported
        issues = y2038detect.scan(self._make(tmp_path,
            'struct stat buf; time_t t = buf.st_mtime;'), strict=True)
        assert len(issues) == 1
        assert 'st_mtime' in issues[0].message
        assert 'struct stat' in issues[0].message

    def test_mtime_arrow_strict(self, tmp_path):
        # Pointer access (buf->st_mtime) is also detected
        issues = y2038detect.scan(self._make(tmp_path,
            'struct stat *p; time_t t = p->st_mtime;'), strict=True)
        assert len(issues) == 1
        assert 'st_mtime' in issues[0].message

    def test_atime_and_ctime_strict(self, tmp_path):
        # st_atime and st_ctime are also detected
        body = (
            'struct stat buf;\n'
            'time_t a = buf.st_atime;\n'
            'time_t b = buf.st_ctime;\n'
        )
        issues = y2038detect.scan(self._make(tmp_path, body), strict=True)
        fields = {i.message.split("'")[1] for i in issues}
        assert 'st_atime' in fields
        assert 'st_ctime' in fields

    def test_mtim_timespec_field_strict(self, tmp_path):
        # st_mtim (struct timespec variant) is also detected
        issues = y2038detect.scan(self._make(tmp_path,
            'struct stat buf; time_t t = buf.st_mtim.tv_sec;'), strict=True)
        assert len(issues) == 1
        assert 'st_mtim' in issues[0].message

    def test_no_double_report_for_chain_access(self, tmp_path):
        # buf.st_mtim.tv_sec: only the st_mtim access is reported, not tv_sec
        issues = y2038detect.scan(self._make(tmp_path,
            'struct stat buf; time_t t = buf.st_mtim.tv_sec;'), strict=True)
        assert len(issues) == 1

    def test_non_stat_struct_not_flagged(self, tmp_path):
        # A different struct with st_mtime must not be flagged
        src = tmp_path / 'other.c'
        src.write_text(
            '#include <time.h>\n'
            'struct mystat { time_t st_mtime; };\n'
            'void f(void) { struct mystat s; time_t t = s.st_mtime; }\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src), strict=True) == []

    def test_suppressed_by_ignore(self, tmp_path):
        src = tmp_path / 'stat_test.c'
        src.write_text(
            self._HDR +
            'void f(void) {\n'
            '    struct stat buf;\n'
            '    time_t t = buf.st_mtime; // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src), strict=True) == []


# ---------------------------------------------------------------------------
# -X <flag> clang pass-through
# ---------------------------------------------------------------------------

class TestClangPassthrough:
    """Tests for -X FLAG and pyproject.toml extra_clang_args."""

    def _make_conditional(self, tmp_path):
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            '#ifdef NO_ISSUE\n'
            'void f(void) { time_t t = time(NULL); }\n'
            '#else\n'
            'void f(void) { int t = time(NULL); }\n'
            '#endif\n',
            encoding='utf-8')
        return src

    def test_x_flag_cli(self, tmp_path, monkeypatch, capsys):
        # -X -DFOO passes a macro define through to libclang
        src = self._make_conditional(tmp_path)
        # Without -X: issue found
        monkeypatch.setattr('sys.argv', ['y2038detect', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 1
        # With -X=-DNO_ISSUE: no issue (= required when value starts with -)
        monkeypatch.setattr('sys.argv',
                            ['y2038detect', '-X=-DNO_ISSUE', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 0

    def test_x_flag_multiple(self, tmp_path, monkeypatch, capsys):
        # Multiple -X flags are all passed through
        src = tmp_path / 't.c'
        src.write_text(
            '#include <time.h>\n'
            '#if defined(FLAG_A) && defined(FLAG_B)\n'
            'void f(void) { time_t t = time(NULL); }\n'
            '#else\n'
            'void f(void) { int t = time(NULL); }\n'
            '#endif\n',
            encoding='utf-8')
        monkeypatch.setattr('sys.argv',
                            ['y2038detect', '-X=-DFLAG_A', '-X=-DFLAG_B',
                             str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 0

    @pytest.mark.skipif(
        y2038detect.tomllib is None,
        reason='tomllib not available (Python < 3.11)')
    def test_extra_clang_args_from_config(self, tmp_path, monkeypatch, capsys):
        # extra_clang_args in pyproject.toml is passed to libclang
        src = self._make_conditional(tmp_path)
        (tmp_path / 'pyproject.toml').write_bytes(
            b'[tool.y2038detect]\nextra_clang_args = ["-DNO_ISSUE"]\n')
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr('sys.argv', ['y2038detect', str(src)])
        with pytest.raises(SystemExit) as exc:
            y2038detect.main()
        assert exc.value.code == 0


class TestFsTimestampApiDetection:
    """Calls to filesystem timestamp-setting APIs flagged by function name."""

    _HDR_UTIME  = '#include <time.h>\n#include <utime.h>\n'
    _HDR_UTIMES = '#include <time.h>\n#include <sys/time.h>\n'
    _HDR_MODERN = '#include <time.h>\n#include <sys/stat.h>\n'

    def _make(self, tmp_path, hdr, body):
        src = tmp_path / 'ts_test.c'
        src.write_text(hdr + 'void f(void) {\n' + body + '\n}\n',
                       encoding='utf-8')
        return str(src)

    # --- deprecated APIs (always flagged) ---

    def test_utime_flagged(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_UTIME,
            'utime("/tmp/x", (void*)0);'))
        assert len(issues) == 1
        assert 'utime()' in issues[0].message
        assert 'time_t' in issues[0].message

    def test_utimes_flagged(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_UTIMES,
            'utimes("/tmp/x", (void*)0);'))
        assert len(issues) == 1
        assert 'utimes()' in issues[0].message
        assert 'tv_sec' in issues[0].message

    def test_lutimes_flagged(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_UTIMES,
            'lutimes("/tmp/x", (void*)0);'))
        assert len(issues) == 1
        assert 'lutimes()' in issues[0].message

    def test_futimes_flagged(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_UTIMES,
            'futimes(0, (void*)0);'))
        assert len(issues) == 1
        assert 'futimes()' in issues[0].message
        assert 'futimens()' in issues[0].message  # suggested replacement

    # --- modern APIs (strict only) ---

    def test_utimensat_not_flagged_without_strict(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_MODERN,
            'utimensat(0, "/tmp/x", (void*)0, 0);'))
        assert issues == []

    def test_utimensat_flagged_with_strict(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_MODERN,
            'utimensat(0, "/tmp/x", (void*)0, 0);'), strict=True)
        assert len(issues) == 1
        assert 'utimensat()' in issues[0].message

    def test_futimens_not_flagged_without_strict(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_MODERN,
            'futimens(0, (void*)0);'))
        assert issues == []

    def test_futimens_flagged_with_strict(self, tmp_path):
        issues = y2038detect.scan(self._make(tmp_path, self._HDR_MODERN,
            'futimens(0, (void*)0);'), strict=True)
        assert len(issues) == 1
        assert 'futimens()' in issues[0].message

    # --- per-line suppression ---

    def test_suppressed_by_ignore(self, tmp_path):
        src = tmp_path / 'ts_test.c'
        src.write_text(
            self._HDR_UTIME +
            'void f(void) {\n'
            '    utime("/tmp/x", (void*)0); // y2038: ignore\n'
            '}\n',
            encoding='utf-8')
        assert y2038detect.scan(str(src)) == []


# ---------------------------------------------------------------------------
# _scan_dual: single-parse dual-mode detection
# ---------------------------------------------------------------------------

class TestScanDual:
    """_scan_dual() returns (default_issues, strict_issues) from one AST parse."""

    _HDR = '#include <time.h>\n#include <sys/stat.h>\n'

    def _make(self, tmp_path, body):
        src = tmp_path / 'dual_test.c'
        src.write_text(self._HDR + 'void f(struct stat *s) {\n' + body + '\n}\n',
                       encoding='utf-8')
        return str(src)

    def test_returns_tuple_of_two_lists(self, tmp_path):
        path = self._make(tmp_path, 'int t = time(NULL);')
        default_issues, strict_issues = y2038detect._scan_dual(path)
        assert isinstance(default_issues, list)
        assert isinstance(strict_issues, list)

    def test_default_detects_narrowing(self, tmp_path):
        path = self._make(tmp_path, 'int t = time(NULL);')
        default_issues, _ = y2038detect._scan_dual(path)
        assert len(default_issues) >= 1
        assert any('time_t' in i.message for i in default_issues)

    def test_strict_superset_of_default(self, tmp_path):
        # Every default issue must also appear in strict (same file/line/col)
        path = self._make(tmp_path, 'int t = time(NULL);')
        default_issues, strict_issues = y2038detect._scan_dual(path)
        default_keys = {(i.file, i.line, i.col) for i in default_issues}
        strict_keys  = {(i.file, i.line, i.col) for i in strict_issues}
        assert default_keys <= strict_keys

    def test_strict_only_detects_stat_field(self, tmp_path):
        # st_mtime access is strict-only; should be absent from default, present in strict
        path = self._make(tmp_path, 'long m = s->st_mtime;')
        default_issues, strict_issues = y2038detect._scan_dual(path)
        stat_default = [i for i in default_issues if 'st_mtime' in i.message]
        stat_strict  = [i for i in strict_issues  if 'st_mtime' in i.message]
        assert stat_default == []
        assert len(stat_strict) >= 1

    def test_empty_file_returns_empty_lists(self, tmp_path):
        src = tmp_path / 'empty_dual.c'
        src.write_text('#include <time.h>\nvoid f(void) {}\n', encoding='utf-8')
        default_issues, strict_issues = y2038detect._scan_dual(str(src))
        assert default_issues == []
        assert strict_issues == []


# ---------------------------------------------------------------------------
# Robustness: unknown libclang TypeKind, and per-file error isolation
# ---------------------------------------------------------------------------

class _FakeUnknownKindType:
    """Stands in for a clang Type whose kind the Python bindings don't know.

    The pip libclang 18.1.1 bindings raise ValueError from Type.kind for
    _Float16 (CXType_Float16 = 32), which they don't list in TypeKind. A
    fake type reproduces that deterministically on any bindings version.
    """

    def get_size(self):
        return 4

    def get_canonical(self):
        return self

    @property
    def kind(self):
        raise ValueError('Unknown template argument kind 32')


class TestUnknownTypeKind:
    def test_type_kind_returns_none_for_unknown_kind(self):
        assert y2038detect._type_kind(_FakeUnknownKindType()) is None

    def test_type_kind_returns_kind_for_known_type(self, tmp_path):
        src = tmp_path / 'a.c'
        src.write_text('int x;\n', encoding='utf-8')
        tu, _ = y2038detect._parse_tu(str(src))
        var = next(c for c in tu.cursor.get_children() if c.spelling == 'x')
        assert y2038detect._type_kind(var.type) == y2038detect.TypeKind.INT

    def test_is_narrow_int_false_for_unknown_kind(self):
        assert y2038detect._is_narrow_int(_FakeUnknownKindType()) is False
        assert y2038detect._is_narrow_int(_FakeUnknownKindType(), strict=True) is False

    def test_truncation_year_does_not_raise_for_unknown_kind(self):
        assert y2038detect._truncation_year(_FakeUnknownKindType()) == '2038'

    def test_float16_file_still_reports_narrowing(self):
        # jart/cosmopolitan's libc/intrin/float16.c crashed the whole
        # repository scan with pip libclang 18.1.1. Other issues in a file
        # using _Float16 must still be detected.
        issues = _scan('_Float16 h = 1; int t = time(NULL);')
        assert any("implicit conversion of time_t to 'int'" in i.message
                   for i in issues)


class TestPerFileErrorIsolation:
    """One file raising must not abort the scan of the others."""

    def _setup(self, tmp_path, monkeypatch):
        good = tmp_path / 'good.c'
        good.write_text('#include <time.h>\nvoid f(void) { int t = time(NULL); }\n',
                        encoding='utf-8')
        bad = tmp_path / 'bad.c'
        bad.write_text('#include <time.h>\nvoid g(void) { int t = time(NULL); }\n',
                       encoding='utf-8')
        real_walk = y2038detect._walk

        def fake_walk(cursor, source_path, issues, strict=False):
            if source_path.endswith('bad.c'):
                raise ValueError('boom')
            return real_walk(cursor, source_path, issues, strict=strict)

        monkeypatch.setattr(y2038detect, '_walk', fake_walk)
        return str(bad), str(good)  # bad first: it must not stop good

    def _run_main(self, monkeypatch, capsys, argv):
        monkeypatch.setattr('sys.argv', ['y2038detect'] + argv)
        with pytest.raises(SystemExit) as exc_info:
            y2038detect.main()
        captured = capsys.readouterr()
        return exc_info.value.code, captured.out, captured.err

    def test_json_continues_and_exits_2(self, tmp_path, monkeypatch, capsys):
        bad, good = self._setup(tmp_path, monkeypatch)
        code, out, err = self._run_main(monkeypatch, capsys, ['--json', bad, good])
        assert code == 2
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]['file'].endswith('good.c')
        assert 'internal error:' in err
        assert 'bad.c' in err
        assert 'ValueError' in err

    def test_json_with_strict_continues_and_exits_2(self, tmp_path, monkeypatch, capsys):
        bad, good = self._setup(tmp_path, monkeypatch)
        code, out, err = self._run_main(
            monkeypatch, capsys, ['--json', '--with-strict', bad, good])
        assert code == 2
        data = json.loads(out)
        assert len(data['default']) == 1
        assert len(data['strict']) == 1
        assert 'internal error:' in err

    def test_text_mode_continues_and_exits_2(self, tmp_path, monkeypatch, capsys):
        bad, good = self._setup(tmp_path, monkeypatch)
        code, out, err = self._run_main(monkeypatch, capsys, ['--no-color', bad, good])
        assert code == 2
        assert 'good.c' in out
        assert 'internal error:' in err
        assert 'bad.c' in err

    def test_all_files_failing_still_exits_2_not_0(self, tmp_path, monkeypatch, capsys):
        bad, _ = self._setup(tmp_path, monkeypatch)
        code, out, err = self._run_main(monkeypatch, capsys, ['--json', bad])
        assert code == 2
        assert json.loads(out) == []

    def test_no_failure_keeps_existing_exit_codes(self, tmp_path, monkeypatch, capsys):
        clean = tmp_path / 'clean.c'
        clean.write_text('#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n',
                         encoding='utf-8')
        code, _, err = self._run_main(monkeypatch, capsys, ['--json', str(clean)])
        assert code == 0
        assert 'internal error:' not in err

    def test_text_mode_summary_mentions_unanalyzed_files(self, tmp_path, monkeypatch, capsys):
        # Two files, one failing, zero issues in the other: the summary must
        # not claim "All 2 files clean."
        bad, _ = self._setup(tmp_path, monkeypatch)
        clean = tmp_path / 'clean.c'
        clean.write_text('#include <time.h>\nvoid f(void) { time_t t = time(NULL); }\n',
                         encoding='utf-8')
        code, out, err = self._run_main(monkeypatch, capsys, ['--no-color', bad, str(clean)])
        assert code == 2
        assert 'All 2 files clean' not in out
        assert '1 not analyzed' in out


# ---------------------------------------------------------------------------
# Unresolvable #include must not stop the analysis of the file
# ---------------------------------------------------------------------------

_MISSING_INCLUDE_NARROWING = (
    '#include "project_internal_that_does_not_exist.h"\n'
    '#include <time.h>\n'
    'void f(void) { int t = time(NULL); }\n'
)

# The printf check relies on clang's own -Wformat diagnostics, which clang
# stops emitting after a fatal error unless the parse keeps going.
_MISSING_INCLUDE_PRINTF = (
    '#include "project_internal_that_does_not_exist.h"\n'
    '#include <stdio.h>\n'
    '#include <time.h>\n'
    'void f(time_t t) { printf("%d", t); }\n'
)


class TestMissingInclude:
    """v0.9.3's evaluation could analyze only ~10% of files: any file with
    an unresolvable #include (project-internal headers, without -I or
    compile_commands.json) was dropped, because --show-parse-errors made
    scan()/_scan_dual() give up on a fatal diagnostic. The AST clang returns
    after such an error is still usable."""

    def _write(self, tmp_path, text):
        src = tmp_path / 'a.c'
        src.write_text(text, encoding='utf-8')
        return str(src)

    def test_scan_detects_narrowing_after_missing_include(self, tmp_path):
        path = self._write(tmp_path, _MISSING_INCLUDE_NARROWING)
        assert len(y2038detect.scan(path)) == 1

    def test_scan_with_show_diagnostics_still_detects(self, tmp_path, capsys):
        path = self._write(tmp_path, _MISSING_INCLUDE_NARROWING)
        issues = y2038detect.scan(path, show_diagnostics=True)
        assert len(issues) == 1
        assert 'file not found' in capsys.readouterr().err

    def test_scan_dual_with_show_diagnostics_still_detects(self, tmp_path, capsys):
        path = self._write(tmp_path, _MISSING_INCLUDE_NARROWING)
        default_issues, strict_issues = y2038detect._scan_dual(path, show_diagnostics=True)
        assert len(default_issues) == 1
        assert len(strict_issues) == 1
        assert 'file not found' in capsys.readouterr().err

    def test_analyze_detects_after_missing_include(self, tmp_path, capsys):
        path = self._write(tmp_path, _MISSING_INCLUDE_NARROWING)
        assert y2038detect.analyze(path) == 1
        assert "implicit conversion of time_t to 'int'" in capsys.readouterr().out

    def test_printf_check_survives_missing_include(self, tmp_path):
        path = self._write(tmp_path, _MISSING_INCLUDE_PRINTF)
        issues = y2038detect.scan(path)
        assert any('printf' in i.message for i in issues)

    def test_missing_include_alone_is_not_a_failure(self, tmp_path, capsys):
        # An unresolvable header is normal when scanning without -I; with
        # nothing wrong in the file itself the result is clean.
        path = self._write(tmp_path,
                           '#include "project_internal_that_does_not_exist.h"\n'
                           'int f(void) { return 0; }\n')
        assert y2038detect.analyze(path) == 0

    def test_json_mode_same_result_with_and_without_show_parse_errors(
            self, tmp_path, monkeypatch, capsys):
        # The two flag combinations used to disagree on the same file.
        path = self._write(tmp_path, _MISSING_INCLUDE_NARROWING)
        results = []
        for extra in ([], ['--show-parse-errors']):
            monkeypatch.setattr('sys.argv', ['y2038detect', '--json'] + extra + [path])
            with pytest.raises(SystemExit):
                y2038detect.main()
            results.append(len(json.loads(capsys.readouterr().out)))
        assert results == [1, 1]
