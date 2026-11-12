#!/usr/bin/env python3
"""
make_scan_log.py — run y2038detect and generate an evaluation scan log.

Usage:
    python make_scan_log.py PROJECT VERSION -- [y2038detect args...]

Example:
    python make_scan_log.py nginx 1.31.1 -- \\
        --no-system-includes \\
        -I /tmp/nginx_stubs \\
        -I nginx-1.31.1/src/core \\
        nginx-1.31.1/src/

Output:
    evaluation/logs/{PROJECT}-{VERSION}.md
    (use --output to override)
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _version import __version__ as _DETECT_VERSION

_RE_SUMMARY = re.compile(r'^(\d+) issues? in \d+ files? \((\d+) clean\)')
_RE_WARNING = re.compile(r'^(.+):(\d+):\d+: warning: (.+)')
_RE_FATAL   = re.compile(r'^fatal: ')
_RE_CAST    = re.compile(r'(implicit|explicit) conversion of (\S+) to \'([^\']+)\'')

_KIND_JA = {
    'implicit':   '暗黙変換',
    'explicit':   '明示キャスト',
    'tm_year':    'tm_year 上限',
    'comparison': '定数比較',
}


def parse_output(stdout, stderr):
    """Parse y2038detect stdout/stderr into structured data."""
    warnings = []
    summary = {'total_issues': 0, 'clean': 0}

    lines = stdout.splitlines()
    i = 0
    while i < len(lines):
        m = _RE_SUMMARY.match(lines[i])
        if m:
            summary['total_issues'] = int(m.group(1))
            summary['clean'] = int(m.group(2))
            i += 1
            continue

        m = _RE_WARNING.match(lines[i])
        if m:
            file_path = m.group(1)
            lineno    = int(m.group(2))
            message   = m.group(3)
            code  = lines[i + 1] if i + 1 < len(lines) else ''
            caret = lines[i + 2] if i + 2 < len(lines) else ''
            warnings.append({
                'file': file_path,
                'line': lineno,
                'message': message,
                'raw': '\n'.join([lines[i], code, caret]),
            })
            i += 3
            continue

        i += 1

    seen = set()
    fatal_msgs = []
    for line in stderr.splitlines():
        if _RE_FATAL.match(line) and line not in seen:
            seen.add(line)
            fatal_msgs.append(line.removeprefix('fatal: '))

    summary['y2038_count'] = len(warnings)
    summary['fatal_count'] = summary['total_issues'] - len(warnings)
    return warnings, sorted(fatal_msgs), summary


def classify_warning(message):
    """Return (kind, src_type, dst_type) from a warning message string."""
    m = _RE_CAST.search(message)
    if m:
        return m.group(1), m.group(2), m.group(3)
    if 'tm_year' in message:
        return 'tm_year', 'int (tm_year)', 'int'
    if 'comparison of time_t' in message:
        return 'comparison', 'time_t', 'constant'
    return 'unknown', '?', '?'


def build_options_summary(detect_args):
    """Split detect_args into (strict, other_opts, dux_flags) strings."""
    strict = 'あり' if '--strict' in detect_args else 'なし'

    dux = []
    other = []
    i = 0
    while i < len(detect_args):
        a = detect_args[i]

        if a == '-I' and i + 1 < len(detect_args):
            i += 2
            continue
        if a.startswith('-I'):
            i += 1
            continue

        if a in ('-D', '-U') and i + 1 < len(detect_args):
            dux.append(f'{a} {detect_args[i + 1]}')
            i += 2
            continue
        if re.match(r'^-[DU].', a):
            dux.append(a)
            i += 1
            continue

        if a == '-X' and i + 1 < len(detect_args):
            dux.append(f'-X {detect_args[i + 1]}')
            i += 2
            continue
        if re.match(r'^-X.', a):
            dux.append(a)
            i += 1
            continue

        if a == '--strict' or not a.startswith('-'):
            i += 1
            continue

        other.append(a)
        i += 1

    return strict, ' '.join(other) or 'なし', ' '.join(dux) or 'なし'


def format_command(detect_args):
    """Format detect_args as a readable multi-line shell command.

    Pairs single-char options (-I, -D, -U, -X) with their values so they
    appear on one line instead of being split across two lines.
    """
    tokens = []
    i = 0
    while i < len(detect_args):
        a = detect_args[i]
        if a in ('-I', '-D', '-U', '-X') and i + 1 < len(detect_args):
            tokens.append(f'{a} {detect_args[i + 1]}')
            i += 2
        else:
            tokens.append(a)
            i += 1
    return 'python y2038detect.py \\\n  ' + ' \\\n  '.join(tokens)


def extract_code_context(file_path, line, before=6, after=2):
    """Return a code snippet around the given 1-based line number.

    Returns None if the file cannot be read.
    Shows `before` lines before and `after` lines after the warning line,
    with a '>' marker on the warning line itself.

    before=6/after=2 is a magic number with no recorded reasoning (added
    2026-05-25, commit 3b93dfe). y2038detect.py's own
    _source_context_from_lines() copies these same defaults so the two
    functions' output looks the same in
    evaluation/scripts/05_generate_findings.py; confirmed with the user
    (2026-09-28) that this asymmetry can be changed if a real reason comes
    up, but update both functions' defaults together if so.
    """
    try:
        src = Path(file_path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None

    lines = src.splitlines()
    first = max(0, line - 1 - before)
    last  = min(len(lines), line + after)

    snippet = []
    for i, text in enumerate(lines[first:last], start=first + 1):
        prefix = '>' if i == line else ' '
        snippet.append(f'{prefix} {i:4d}  {text}')
    return '\n'.join(snippet)


def generate_markdown(project, version, detect_args, warnings, fatal_msgs, summary):
    strict, other_opts, dux_flags = build_options_summary(detect_args)
    today = date.today().isoformat()
    cmd_str = format_command(detect_args)
    total = summary['clean'] + summary['total_issues']

    if warnings:
        parts = []
        for idx, w in enumerate(warnings, 1):
            kind, src_t, dst_t = classify_warning(w['message'])
            kind_ja = _KIND_JA.get(kind, kind)

            code_section = ''
            snippet = extract_code_context(w['file'], w['line'])
            if snippet is not None:
                code_section = f"**コード**:\n\n```c\n{snippet}\n```\n\n"

            parts.append(
                f"### {idx}. `{w['file']}:{w['line']}`\n\n"
                f"**種別**: {kind_ja}（`{src_t}` → `{dst_t}`）\n\n"
                f"{code_section}"
                f"**ツール出力**:\n\n```text\n{w['raw']}\n```\n\n"
                f"**解説**: <!-- TODO: 解説を記入 -->\n\n---\n"
            )
        findings_md = '\n'.join(parts)
    else:
        findings_md = '_なし_\n'

    fatal_section = ''
    if fatal_msgs:
        items = '\n'.join(f'- `{f}`' for f in fatal_msgs)
        fatal_section = f'\n### fatal error の内訳（ユニーク）\n\n{items}\n'

    return (
        f'# {project} {version} — y2038detect scan log\n\n'
        f'## スキャン情報\n\n'
        f'| 項目 | 値 |\n'
        f'|------|----|'
        f'\n| 対象パッケージ | {project} {version} |'
        f'\n| スキャン日 | {today} |'
        f'\n| y2038detect バージョン | {_DETECT_VERSION} |'
        f'\n| `--strict` | {strict} |'
        f'\n| その他のオプション | {other_opts} |'
        f'\n| `-D` / `-U` / `-X` | {dux_flags} |\n\n'
        f'### 実行コマンド\n\n'
        f'```sh\n{cmd_str}\n```\n\n'
        f'### スキャン概要\n\n'
        f'| 結果 | ファイル数 |\n'
        f'|------|-----------|\n'
        f'| クリーン | {summary["clean"]} |\n'
        f'| Y2038 問題あり | {summary["y2038_count"]} |\n'
        f'| fatal error | {summary["fatal_count"]} |\n'
        f'| 合計 | {total} |\n'
        f'{fatal_section}\n'
        f'---\n\n'
        f'## 検出された Y2038 問題\n\n'
        f'{findings_md}'
    )


def main():
    p = argparse.ArgumentParser(
        description='Run y2038detect and generate an evaluation scan log.',
        epilog='Pass y2038detect arguments after --',
    )
    p.add_argument('project', help='Project name (e.g. nginx)')
    p.add_argument('version', help='Project version (e.g. 1.31.1)')
    p.add_argument('--output', '-o',
                   help='Output path (default: evaluation/logs/{project}-{version}.md)')
    p.add_argument('--force', '-f', action='store_true',
                   help='Overwrite output file if it already exists')

    # parse_known_args so that --output/--force before '--' are handled correctly
    # even when argparse.REMAINDER would otherwise consume them
    args, rest = p.parse_known_args()
    if rest and rest[0] == '--':
        rest = rest[1:]
    detect_args = rest
    if not detect_args:
        p.error('Specify y2038detect arguments after --')

    out_path = Path(args.output or f'evaluation/logs/{args.project}-{args.version}.md')

    if out_path.exists() and not args.force:
        print(f'error: {out_path} already exists (use --force to overwrite)', file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, 'y2038detect.py'] + detect_args
    print(f'Running y2038detect on {args.project} {args.version} ...', file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)

    warnings, fatal_msgs, summary = parse_output(result.stdout, result.stderr)
    md = generate_markdown(args.project, args.version, detect_args,
                           warnings, fatal_msgs, summary)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding='utf-8')

    print(f'Written: {out_path}', file=sys.stderr)
    print(
        f"  Y2038: {summary['y2038_count']}, "
        f"fatal: {summary['fatal_count']}, "
        f"clean: {summary['clean']}",
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
