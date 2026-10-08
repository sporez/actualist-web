#!/usr/bin/env python3
"""Set the homepage's latest-build line from the newest TestFlight release.

Reads GitHub releases for sporez/actualist, picks the newest published
`testflight/v<version>-b<build>` tag, and rewrites the text between the
`<!-- build -->` markers in public/index.html. Prints what it did and exits 0
whether or not anything changed. Uses GITHUB_TOKEN if set.
"""
import datetime
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO = "sporez/actualist"
INDEX = Path(__file__).resolve().parent.parent / "public" / "index.html"
TAG = re.compile(r"^testflight/v(?P<version>[\d.]+)-b(?P<build>\d+)$")
MARKERS = re.compile(r"(<!-- build -->).*?(<!-- /build -->)", re.S)


def latest_release():
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases?per_page=20",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "actualist-web"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        releases = json.load(response)
    for release in releases:
        match = TAG.match(release.get("tag_name", ""))
        if match and not release.get("draft") and release.get("published_at"):
            return release, match
    sys.exit("No published TestFlight release found")


def main():
    release, match = latest_release()
    published = datetime.datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
    date = f"{published:%B} {published.day}, {published.year}"
    line = (
        f'<a href="https://github.com/{REPO}/releases/tag/{release["tag_name"]}">'
        f'{match["version"]} ({match["build"]})</a> · {date}'
    )
    html = INDEX.read_text()
    if not MARKERS.search(html):
        sys.exit("Build markers missing from public/index.html")
    updated = MARKERS.sub(lambda m: f"{m[1]}{line}{m[2]}", html)
    if updated == html:
        print(f"Already current: {match['version']} ({match['build']})")
        return
    INDEX.write_text(updated)
    print(f"Updated to {match['version']} ({match['build']}) · {date}")


if __name__ == "__main__":
    main()
