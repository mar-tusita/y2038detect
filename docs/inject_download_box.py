#!/usr/bin/env python3
"""Replace <!-- download-box --> in the generated HTML with the actual download box.

Usage: inject_download_box.py VERSION HTML_FILE [LANG]

The button links to the zip attached to the GitHub Release of the public
repository (.github/workflows/release.yml attaches it), not to a copy on the
Pages site. The URL is fixed to the public repository so that the preview
site of the development repository links to the same zip.
Deploy Pages only after the Release for VERSION has its zip, or the link is
broken until then.
"""
import pathlib
import sys

RELEASES_URL = 'https://github.com/mar-tusita/y2038detect/releases'
MARKER = '<!-- download-box -->'


def release_zip_url(version):
    """URL of the zip attached to the GitHub Release vVERSION."""
    return f'{RELEASES_URL}/download/v{version}/y2038detect-{version}.zip'


def download_box(version, lang):
    """HTML of the download box for lang ('ja' or 'en')."""
    url = release_zip_url(version)
    if lang == 'en':
        label = f'&#11015; Download (v{version})'
        note = 'Requires Python 3.10+ and libclang'
    elif lang == 'ja':
        label = f'&#11015; ダウンロード (v{version})'
        note = 'Python 3.10 以上・libclang が必要'
    else:
        raise ValueError(f'unknown language: {lang}')
    return f'''\
<div class="download-box">
  <span class="version-badge">v{version}</span><br>
  <a class="btn-download" href="{url}">{label}</a>
  <p class="download-note">{note}</p>
</div>'''


def main(argv):
    if len(argv) not in (3, 4):
        sys.exit('usage: inject_download_box.py VERSION HTML_FILE [LANG]')
    version = argv[1]
    html_file = pathlib.Path(argv[2])
    lang = 'ja'
    if len(argv) == 4:
        lang = argv[3]

    content = html_file.read_text(encoding='utf-8')
    if MARKER not in content:
        sys.exit(f'error: {MARKER} not found in {html_file}')
    content = content.replace(MARKER, download_box(version, lang))
    html_file.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv)
