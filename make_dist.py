#!/usr/bin/env python3
"""Create a distribution zip for y2038detect."""

import datetime
import os
import zipfile

# Read version from the single source of truth
import importlib.util
_spec = importlib.util.spec_from_file_location('_version', '_version.py')
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
VERSION = _mod.__version__

DATE      = datetime.date.today().strftime('%Y%m%d')
DIST_NAME = f'y2038detect-{VERSION}-{DATE}'
DIST_ZIP  = os.path.join('dist', f'{DIST_NAME}.zip')

# Files and directories to include in the zip.
# y2038detect.py is handled separately (version is embedded at build time).
# _version.py is intentionally omitted: pip install . from the zip is not
# supported (stubs are not installed by pip), so there is no need to keep
# the separate version module.
INCLUDE_FILES = [
    'make_scan_log.py',
    'make_scan_log.md',
    'make_scan_log.en.md',
    'extract_stubs.py',
    'extract_stubs.md',
    'extract_stubs.en.md',
    'pyproject.toml',
    'README.md',
    'LICENSE',
]
INCLUDE_DIRS = [
    '_stubs',
    '_stubs_freebsd',
    '_stubs_linux',
]


def main() -> None:
    os.makedirs('dist', exist_ok=True)

    with zipfile.ZipFile(DIST_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Embed version into y2038detect.py so it needs no _version.py at runtime
        src = open('y2038detect.py', encoding='utf-8').read()
        src = src.replace(
            'from _version import __version__',
            f"__version__ = '{VERSION}'",
        )
        zf.writestr(f'{DIST_NAME}/y2038detect.py', src)
        print(f'  add  {DIST_NAME}/y2038detect.py  (version embedded)')

        for fname in INCLUDE_FILES:
            zf.write(fname, f'{DIST_NAME}/{fname}')
            print(f'  add  {DIST_NAME}/{fname}')

        for dname in INCLUDE_DIRS:
            for root, _, files in os.walk(dname):
                for f in sorted(files):
                    path = os.path.join(root, f)
                    # Use forward slashes in zip entries for cross-platform compatibility
                    arcname = f'{DIST_NAME}/' + path.replace(os.sep, '/')
                    zf.write(path, arcname)
                    print(f'  add  {arcname}')

    size_kb = os.path.getsize(DIST_ZIP) / 1024
    print(f'\nCreated: {DIST_ZIP}  ({size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
