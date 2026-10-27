#!/usr/bin/env python3
"""Set the privacy page from PRIVACY.md at the newest TestFlight release.

Finds the newest published `testflight/v<version>-b<build>` release of
sporez/actualist (the same release `update-build.py` uses), downloads
PRIVACY.md at that tag, and rewrites the text between the `<!-- privacy -->`
markers in public/privacy.html. Reading the release tag, not `main`, means the
site's privacy page changes only when a build with that text is released.

PRIVACY.md may use only `#`/`##` headings, paragraphs, **bold**, `code`, and
[links](url). Anything else (lists, tables, quotes, deeper headings) stops the
script with an error, so a conversion it can't do never reaches the site.
Prints what it did and exits 0 whether or not anything changed. Uses
GITHUB_TOKEN if set. `--file PATH` converts a local PRIVACY.md instead, for a
preview; it never reads a release.
"""
import argparse
import html
import importlib.util
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIVACY_PAGE = ROOT / "public" / "privacy.html"
REPO = "sporez/actualist"
MARKERS = re.compile(r"(<!-- privacy -->\n).*?(\n[ \t]*<!-- /privacy -->)", re.S)
EFFECTIVE = re.compile(r"^Effective (?P<date>.+?)\.$")
UNSUPPORTED = re.compile(r"^(\s*[-*+]\s|\s*\d+[.)]\s|\s*>|\s*\||\s*```|###)")
INDENT = "      "


def latest_release_tag():
    sys.dont_write_bytecode = True  # Loading update-build.py must not leave __pycache__ behind.
    spec = importlib.util.spec_from_file_location("update_build", ROOT / "scripts" / "update-build.py")
    update_build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(update_build)
    release, _ = update_build.latest_release()
    return release["tag_name"]


def fetch_privacy(tag):
    url = f"https://raw.githubusercontent.com/{REPO}/refs/tags/{urllib.parse.quote(tag)}/PRIVACY.md"
    request = urllib.request.Request(url, headers={"User-Agent": "actualist-web"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def inline(text):
    """Escape, then convert **bold**, `code` and [links](url)."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)

    def link(match):
        label, target = match.group(1), match.group(2)
        if not re.match(r"^[a-z]+://", target):
            # Repository-relative links point at the current file on GitHub.
            target = f"https://github.com/{REPO}/blob/main/{target}"
        return f'<a href="{html.escape(target)}">{label}</a>'

    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)
    if re.search(r"[*\[\]]", re.sub(r"<[^>]+>", "", out)):
        sys.exit(f"Unsupported Markdown left in: {text}")
    return out


def convert(markdown):
    """Returns (effective date, HTML body lines)."""
    blocks, current = [], []
    for line in markdown.splitlines():
        if UNSUPPORTED.match(line):
            sys.exit(f"Unsupported Markdown in PRIVACY.md: {line.strip()}")
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    effective, body = None, []
    for block in blocks:
        text = " ".join(block)
        if text.startswith("# "):
            continue  # The page has its own <h1>.
        if text.startswith("## "):
            if len(block) != 1:
                sys.exit(f"Heading spans more than one line: {text}")
            body.append(f"<h2>{inline(text[3:])}</h2>")
            continue
        match = EFFECTIVE.match(text)
        if match and effective is None:
            effective = match.group("date")
            continue
        body.append(f"<p>{inline(text)}</p>")
    if effective is None:
        sys.exit("PRIVACY.md has no 'Effective <date>.' line")
    return effective, body


def render(effective, body):
    meta = (
        f'<p class="meta">Effective {html.escape(effective)}. This is the public copy of '
        f'<a href="https://github.com/{REPO}/blob/main/PRIVACY.md">PRIVACY.md</a> '
        "in the app repository.</p>"
    )
    return "\n".join(INDENT + line for line in [meta, *body])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, help="convert this PRIVACY.md instead of the release's")
    args = parser.parse_args()

    if args.file:
        source, markdown = str(args.file), args.file.read_text(encoding="utf-8")
    else:
        tag = latest_release_tag()
        source, markdown = f"{REPO}@{tag}", fetch_privacy(tag)

    page = PRIVACY_PAGE.read_text(encoding="utf-8")
    if not MARKERS.search(page):
        sys.exit("public/privacy.html is missing the <!-- privacy --> markers")
    effective, body = convert(markdown)
    updated = MARKERS.sub(lambda m: m.group(1) + render(effective, body) + m.group(2), page, count=1)

    if updated == page:
        print(f"Privacy page already matches PRIVACY.md from {source}")
        return
    PRIVACY_PAGE.write_text(updated, encoding="utf-8")
    print(f"Updated privacy page from {source} (effective {effective})")


if __name__ == "__main__":
    main()
