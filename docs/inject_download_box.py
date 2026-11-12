#!/usr/bin/env python3
"""Replace <!-- download-box --> in the generated HTML with the actual download box."""
import sys
import pathlib

version    = sys.argv[1]
html_file  = pathlib.Path(sys.argv[2])
zip_prefix = sys.argv[3] if len(sys.argv) > 3 else ''
lang       = sys.argv[4] if len(sys.argv) > 4 else 'ja'

if lang == 'en':
    box = f'''\
<div class="download-box">
  <span class="version-badge">v{version}</span><br>
  <a class="btn-download" href="{zip_prefix}y2038detect-{version}.zip">&#11015; Download (v{version})</a>
  <p class="download-note">Requires Python 3.10+ and libclang</p>
</div>'''
else:
    box = f'''\
<div class="download-box">
  <span class="version-badge">v{version}</span><br>
  <a class="btn-download" href="{zip_prefix}y2038detect-{version}.zip">&#11015; ダウンロード (v{version})</a>
  <p class="download-note">Python 3.10 以上・libclang が必要</p>
</div>'''

content = html_file.read_text(encoding='utf-8')
content = content.replace('<!-- download-box -->', box)
html_file.write_text(content, encoding='utf-8')
