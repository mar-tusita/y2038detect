"""sitemap.xml を生成するスクリプト。deploy-pages.yml から呼ばれる。"""
import sys
import datetime

BASE = "https://mar-tusita.github.io/y2038detect"
URLS = [f"{BASE}/", f"{BASE}/en/"]

date = datetime.date.today().isoformat()

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for url in URLS:
    lines += [
        "  <url>",
        f"    <loc>{url}</loc>",
        f"    <lastmod>{date}</lastmod>",
        "  </url>",
    ]
lines += ["</urlset>", ""]

out = sys.argv[1] if len(sys.argv) > 1 else "_site/sitemap.xml"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
