# extract_stubs.py

A tool for generating minimal C stubs when scanning fails due to missing headers — whether platform-specific headers not covered by the bundled stubs, or project-specific third-party headers.

## Usage

```bash
python extract_stubs.py --outdir my_stubs some_header.h sys/platform.h
```

Then pass the generated stubs to the scanner with `-I`:

```bash
python y2038detect.py -I my_stubs src/
```

## Requirements

Run on a system where the target headers actually exist, since the script uses libclang to parse them. Linux or FreeBSD is recommended; running on Windows is not supported due to system header compatibility issues.

## Known Limitations

Output is auto-generated; review it before use. It has the following limitations. None of them affects detection by y2038detect.

- **Anonymous sub-structs/unions**: a struct that contains an unnamed struct or union produces broken output such as `struct (unnamed struct at ...)`, and field references may be broken.
- **Unrelated macros**: macros from headers that the given header includes indirectly are picked up too, so the output may contain many unrelated macros.
- **K&R function declarations**: a declaration without parameter information is emitted with `(void)` as its parameters.
- **String macros**: macros that define string constants, such as `_PATH_*`, are not emitted.
