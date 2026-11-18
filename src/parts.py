"""HTML building blocks shared by every sheet: accidentals, piano-key note cells, labels."""
import html

from music import is_black


def acc(s):
    """Escape text and wrap ♭ ♯ ♮ 𝄪 so they use the symbol font."""
    s = html.escape(str(s))
    for a in "♭♯♮𝄪":
        s = s.replace(a, f'<span class="acc">{a}</span>')
    return s


def digit(x, hand):
    """A finger number. The thumb (1) gets a ring, drawn as SVG so it stays perfectly round in
    the PDF (a CSS border-radius circle is pixel-snapped there and can come out oval)."""
    if x is None:
        return '<span class="f"></span>'
    if x == 1:
        return (f'<span class="f {hand} th"><svg class="ring" viewBox="0 0 20 20" aria-hidden="true">'
                f'<circle cx="10" cy="10" r="9.2"/></svg><span>1</span></span>')
    return f'<span class="f {hand}">{x}</span>'


def cell(note, rh=None, lh=None, mark=False, rows="both"):
    """One piano key (white or black) with the right-hand finger above and the left-hand finger below.

    rows: 'both', 'rh' (right hand only), 'lh' (left hand only) or 'none' (just the key).
    """
    k = "blk" if is_black(note) else "wht"
    mk = " mk" if mark else ""
    parts = []
    if rows in ("both", "rh"):
        parts.append(digit(rh, "rh"))
    parts.append(f'<span class="n {k}{mk}">{acc(note)}</span>')
    if rows in ("both", "lh"):
        parts.append(digit(lh, "lh"))
    return f'<div class="c c-{rows}">{"".join(parts)}</div>'


def cells(ns, r=None, l=None, rows="both", mark=None):
    """A row of keys, optionally with right-hand fingers above and left-hand fingers below."""
    out = []
    for i, n in enumerate(ns):
        out.append(cell(n, r[i] if r else None, l[i] if l else None, mark == i, rows))
    return f'<div class="cells" style="--n:{len(ns)}">{"".join(out)}</div>'


def key_label(key, small):
    return f'<div class="key"><b>{acc(key)}</b><small>{acc(small)}</small></div>'


def runhead(name, section, num, total):
    return (f'<div class="runhead"><span>{acc(name)}</span><span>{acc(section)}</span>'
            f"<span>{num} / {total}</span></div>")
