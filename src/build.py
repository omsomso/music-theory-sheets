#!/usr/bin/env python3
"""Build every sheet: check its content, then write its HTML.

Usage: python3 src/build.py OUT_DIR
Writes OUT_DIR/index.html (the site's front page) and, for each sheet in SHEETS,
OUT_DIR/<slug>.html (the page content published as the claude.ai artifact),
OUT_DIR/<slug>-preview.html (the same page as a complete document; this is what the
GitHub Pages site serves) and OUT_DIR/<slug>-print.html (fixed A4 pages for the PDF).
Exits non-zero if any check fails.

To add a sheet: create a module like fingering.py (SLUG, TITLE, NAME, DESCRIPTION, PAGES,
validate(), summary()) and add it to SHEETS. The Makefile picks up every *-print.html.
"""
import re
import sys
from pathlib import Path

import fingering
from parts import acc, runhead

SHEETS = [fingering]

CSS = Path(__file__).with_name("sheet.css").read_text(encoding="utf-8")
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900"
         "&family=Inter:wght@400;500;600;700&family=Noto+Sans+Symbols+2&display=swap")
# Full-document head for pages served on their own (the GitHub Pages site and local previews).
# noindex keeps the public site out of search results; it is unlisted, not private.
PREVIEW_HEAD = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<meta name="robots" content="noindex, nofollow">\n')
SITE_TITLE = "Music Theory Sheets"


def index_page():
    """The site's front page: one entry per sheet, linking its web version and PDF."""
    items = "".join(
        f'<li><div><a class="sheet-link" href="{s.SLUG}.html">{s.NAME}</a><p>{s.DESCRIPTION}</p></div>'
        f'<a class="pdf" href="{s.SLUG}.pdf" target="_blank" rel="noopener">PDF · {len(s.PAGES)} A4 pages</a></li>'
        for s in SHEETS
    )
    return (
        PREVIEW_HEAD + f"<title>{SITE_TITLE}</title>\n"
        f'<link rel="stylesheet" href="{FONTS}">\n<style>{CSS}</style>\n'
        "<style>body{margin:0;font-size:14px}</style></head><body>"
        f'<div class="sheet"><header class="top"><div class="title"><h1>{SITE_TITLE}</h1>'
        '<p class="sub">Printable music reference sheets. Open one in the browser, or download the PDF to print.</p>'
        f'</div></header><ul class="sheets">{items}</ul></div></body></html>\n'
    )


def head(sheet):
    return f"""<title>{sheet.TITLE}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
"""


def site_nav(sheet):
    """Top bar on the GitHub Pages version of a sheet: back to the index, and the PDF."""
    return (f'<nav class="sitenav" aria-label="Site"><a class="back" href="index.html">← {SITE_TITLE}</a>'
            f'<a class="pdf" href="{sheet.SLUG}.pdf" target="_blank" rel="noopener">'
            f'PDF · {len(sheet.PAGES)} A4 pages</a></nav>\n')


H2 = re.compile(r"\s*<h2>(.*?)</h2>(.*)", re.S)

# Web only: open or close every section, open the one a #link points to, open all before printing.
WEB_SCRIPT = """<script>
(function () {
  var secs = Array.prototype.slice.call(document.querySelectorAll("details.sec"));
  function setAll(open) { secs.forEach(function (d) { d.open = open; }); }
  var openBtn = document.getElementById("open-all"), closeBtn = document.getElementById("close-all");
  if (openBtn) openBtn.addEventListener("click", function () { setAll(true); });
  if (closeBtn) closeBtn.addEventListener("click", function () { setAll(false); });
  function openFromHash() {
    var id = location.hash.slice(1), d = id && document.getElementById(id);
    if (d && d.tagName === "DETAILS") { d.open = true; d.scrollIntoView(); }
  }
  window.addEventListener("hashchange", openFromHash);
  openFromHash();
  window.addEventListener("beforeprint", function () { setAll(true); });
})();
</script>
"""


def section_id(title):
    text = re.sub(r"<[^>]+>", "", title).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def web_body(sheet):
    """Web layout: every section that starts with an <h2> becomes a closed, expandable block.

    Sections without a title (the header, footnotes) stay visible: before the first block if
    they come first, otherwise after the last one.
    """
    top, blocks, tail = [], [], []
    hints = getattr(sheet, "SECTION_HINTS", {})
    for _, sections in sheet.PAGES:
        for build_section in sections:
            html = build_section()
            m = H2.match(html)
            if not m:
                (tail if blocks else top).append(html)
                continue
            title, body = m.groups()
            hint = hints.get(build_section.__name__, "")
            hint_html = f'<span class="hint">{acc(hint)}</span>' if hint else ""
            blocks.append(
                f'<details class="sec" id="{section_id(title)}"><summary><h2>{title}</h2>{hint_html}</summary>'
                f'<div class="sec-body">{body}</div></details>'
            )
    controls = ('<div class="sec-controls"><button type="button" id="open-all">Open all</button>'
                '<button type="button" id="close-all">Close all</button></div>')
    return "".join(top) + controls + "\n".join(blocks) + "".join(tail)


def render(sheet, print_mode, nav=False):
    """Print: one fixed A4 <section> per page. Web: expandable sections, plus the site bar if nav."""
    if print_mode:
        total = len(sheet.PAGES)
        pages = [
            f'<section class="page p{i}">{runhead(sheet.NAME, name, i, total)}'
            f'{"".join(s() for s in sections)}</section>'
            for i, (name, sections) in enumerate(sheet.PAGES, 1)
        ]
        return '<div class="sheet print">\n' + "\n".join(pages) + "\n</div>\n"
    return ('<div class="sheet web">\n' + (site_nav(sheet) if nav else "") + web_body(sheet)
            + "\n</div>\n" + WEB_SCRIPT)


def validate():
    return [f"{sheet.SLUG}: {p}" for sheet in SHEETS for p in sheet.validate()]


def write_outputs(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(index_page(), encoding="utf-8")
    for sheet in SHEETS:
        page = head(sheet) + render(sheet, False)
        (out_dir / f"{sheet.SLUG}.html").write_text(page, encoding="utf-8")
        (out_dir / f"{sheet.SLUG}-preview.html").write_text(
            PREVIEW_HEAD + head(sheet) + "<style>body{margin:0;font-size:14px}</style></head><body>"
            + render(sheet, False, nav=True) + "</body></html>\n",
            encoding="utf-8",
        )
        (out_dir / f"{sheet.SLUG}-print.html").write_text(
            PREVIEW_HEAD + head(sheet)
            + "<style>html,body{margin:0;padding:0;background:#fff}</style></head><body>"
            + render(sheet, True)
            + "</body></html>\n",
            encoding="utf-8",
        )


def main(argv):
    if len(argv) != 2:
        print("usage: python3 src/build.py OUT_DIR")
        return 2
    problems = validate()
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    for sheet in SHEETS:
        print(f"{sheet.SLUG}: all checks pass ({sheet.summary()})")
    write_outputs(argv[1])
    print("wrote", ", ".join(f"{s.SLUG}.html" for s in SHEETS), "(+ -preview, -print) to", argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
