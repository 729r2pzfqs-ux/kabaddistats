#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Submit kabaddistats.com URLs to IndexNow (Bing, Yandex, et al.).

IndexNow lets the site proactively tell search engines which URLs changed
instead of waiting for a crawl. Ownership is proved by hosting a key file at
https://kabaddistats.com/<key>.txt whose contents equal the key.

Usage:
    python scripts/indexnow.py                # submit every URL in sitemap.xml
    python scripts/indexnow.py URL [URL ...]  # submit specific URLs
    python scripts/indexnow.py --dry-run      # print the payload, don't send

The bulk endpoint accepts up to 10,000 URLs per request; we chunk to stay
under that limit.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "kabaddistats.com"
SITE = f"https://{HOST}"
KEY = "9d4e1f7a2c6b48e0a3f5c1d9b7e6a204"
ENDPOINT = "https://api.indexnow.org/indexnow"
CHUNK = 10000

ROOT = Path(__file__).resolve().parent.parent


def sitemap_urls():
    """Read every <loc> out of the generated sitemap.xml."""
    sm = ROOT / "sitemap.xml"
    if not sm.exists():
        sys.exit("sitemap.xml not found — run scripts/generate.py first.")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(sm.read_text(encoding="utf-8"))
    return [loc.text for loc in root.iterfind(".//s:loc", ns) if loc.text]


def submit(urls):
    """POST a batch of URLs to the IndexNow bulk endpoint."""
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{SITE}/{KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            # IndexNow rejects the default Python-urllib agent with 403.
            "User-Agent": "Mozilla/5.0 (compatible; kabaddistats-indexnow/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if not a.startswith("--")]
    urls = args if args else sitemap_urls()
    print(f"{len(urls)} URL(s) to submit to IndexNow.")
    if dry:
        for u in urls[:20]:
            print("  ", u)
        if len(urls) > 20:
            print(f"   … and {len(urls) - 20} more")
        return
    for i in range(0, len(urls), CHUNK):
        batch = urls[i:i + CHUNK]
        status, body = submit(batch)
        print(f"  batch {i // CHUNK + 1}: HTTP {status} "
              f"({len(batch)} URLs) {body.strip()[:120]}")


if __name__ == "__main__":
    main(sys.argv[1:])
