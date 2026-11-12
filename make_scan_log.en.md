# make_scan_log.py

A tool for recording scan results across multiple projects in a reproducible Markdown format.

## Usage

```bash
python make_scan_log.py PROJECT VERSION -- [y2038detect options] SOURCE_PATH
```

Output: `evaluation/logs/{PROJECT}-{VERSION}.md` (override with `--output`). Use `--force` to overwrite an existing file.

**Example (scanning nginx 1.31.1):**

```bash
python make_scan_log.py nginx 1.31.1 -- \
    --no-system-includes \
    -I /path/to/nginx_stubs \
    -I nginx-1.31.1/src/core \
    -I nginx-1.31.1/src/os/unix \
    nginx-1.31.1/src/
```

## Generated File Contents

- Metadata table: scan date, y2038detect version, options used
- Exact command for reproduction
- File count summary: clean / issues / fatal errors
- List of unique fatal error causes
- Code context (with `>` marker) and tool output for each finding

Each finding includes a `**解説**: <!-- TODO: 解説を記入 -->` placeholder where you can add an explanation of the issue's meaning and impact.
