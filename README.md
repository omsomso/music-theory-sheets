# Music Theory Sheets

Printable music reference sheets, generated from checked data. Each sheet is a set of A4 pages
(PDF) and a web page.

**Site:** <https://omsomso.github.io/music-theory-sheets/>. It opens anywhere without a
login. It is unlisted, not private: every page asks search engines not to index it, but
anyone with the link can open it. (Login-protected Pages sites need GitHub Enterprise Cloud.)
The repository itself stays private.

| Sheet | Web | PDF |
| --- | --- | --- |
| Piano Fingering | [site](https://omsomso.github.io/music-theory-sheets/piano-fingering.html) | [`docs/piano-fingering.pdf`](docs/piano-fingering.pdf) |

## Piano Fingering

Six A4 pages:

- **Page 1:** major scales in all 12 keys.
- **Page 2:** natural and harmonic minor scales in all 12 keys.
- **Page 3:** the two melodic minor scales (F♯ and C♯) that need a different right-hand
  fingering; the chromatic scale, standard and a faster right-hand version in groups of
  1 2 3 / 1 2 3 4; pentatonic, blues, whole-tone and diminished scales (notes and difference
  from major; they have no standard fingering).
- **Page 4:** the seven modes in mode order, with a strip showing which white key starts
  each one, and six jazz scales (melodic minor, Lydian dominant, Mixolydian ♭6, Locrian ♮2,
  Altered, Phrygian dominant), all on C with fingering for both hands and their difference
  from major.
- **Page 5:** arpeggios in all 24 major and minor keys, C major and G♯ minor written out over
  two octaves, and a side column with inversions and the left hand's 3-or-4 rule.
- **Page 6, chords:** block chords (triads and four-note chords in every inversion; sus2,
  sus4, add9 and 6th shapes), 22 chord types with formulas, and two-hand voicings for
  9th/11th/13th chords.

The fingerings for modes and jazz scales aren't copied from a book: `auto_fingering()` works
them out with the rules behind standard scale fingering (thumbs on white keys, preferably
right after a black key, in groups of three and four fingers). The build checks that those
same rules reproduce every hand-written major and minor fingering on pages 1–2.

Every note is drawn as a white or black key. The right-hand finger sits above it and the
left-hand finger below. Thumbs are circled, so you can see where the hand crosses. Each
scale and arpeggio sits in its own band, shaded on alternate rows. Colours are neutral
greys with muted blue and red, kept low in contrast so the pages are easy on the eye.

Each page is made of sections (`sec_*` functions in `src/fingering.py`); `PAGES` at the end
of that file decides which sections share a page.

On the web every section with a title is a closed,
expandable block, with **Open all** / **Close all** buttons and a one-line hint per section
(`SECTION_HINTS`). A link such as `piano-fingering.html#modes` opens that section. The PDF
keeps its fixed pages.

## How it's built

Each sheet is a Python module in `src/` holding its data tables, the checks for that data, and
its page layouts. `src/build.py` lists the sheets in `SHEETS`, runs every check and writes the
HTML. Two small WebKit tools render and check the result.

```text
src/build.py            builds every sheet listed in SHEETS
src/fingering.py        the Piano Fingering sheet: data, checks, pages
src/music.py            shared pitch helpers (pitch classes, black keys, half steps)
src/parts.py            shared HTML pieces (piano-key note cells, labels, running heads)
src/sheet.css           shared styles, including the fixed A4 print layout
src/render.swift        renders a sheet's print HTML to A4 pages; fails if a page overflows
src/phone_check.swift   loads a sheet's web page at phone width; fails if anything sticks out
tests/test_build.py     checks pass on the real data and catch planted mistakes
docs/                   the GitHub Pages site: index.html, <sheet>.html, <sheet>.pdf (committed)
build/                  everything else, incl. <sheet>.html without a wrapper; not committed
```

Requirements: macOS with the Xcode command line tools (`swiftc`), Python 3.9 or later
(standard library only), and a network connection while rendering (fonts come from Google
Fonts).

```sh
make          # tests, PDFs, phone-width check
make test     # tests only
make pdf      # rebuild the docs/ site: index, each sheet's page and PDF
make phone    # phone-width check with every section open; snapshots in build/<sheet>-phone-*.png
make clean
```

`make pdf` prints how much of each 842 px page is used, which helps when moving sections
between pages. `build/<sheet>-page-*.png` are previews of each printed page, and
`build/<sheet>-preview.html` opens in any browser.

### Publishing

- **Site:** GitHub Pages serves the `docs/` folder of `main`. Run `make`, commit `docs/` and
  push; the site updates about a minute later.
- **Private web copy:** `build/<sheet>.html` is the same page without a document wrapper,
  for hosts that add their own. Where it's published is noted in `LOCAL.md`, which is
  kept out of the repository.

### Adding a sheet

1. Create `src/<name>.py` with `SLUG` (output file name), `TITLE` (page title), `NAME`
   (running head and index entry), `DESCRIPTION` (one line for the index), `PAGES` (a list of
   `(section name, function returning page HTML)`, one per A4 page), `validate()` (returns a
   list of problems) and `summary()`.
2. Add the module to `SHEETS` in `src/build.py`. The site index lists it automatically.
3. Add tests that plant a mistake in its data and expect `validate()` to catch it.
4. Run `make`, look at `build/<slug>-page-*.png`, and add the sheet to the table above.

## What the fingering checks cover

`fingering.validate()` stops the build if any of these fail:

- Scale notes match the major or natural-minor step pattern and are spelled with
  consecutive letters.
- No scale or chord puts the thumb on a black key. The only exceptions are arpeggios whose
  notes are all black keys (F♯ major, E♭ minor).
- Finger order is playable: the thumb passes under after 2, 3 or 4, and a finger crosses
  over the thumb going the other way.
- Every arpeggio still works when extended to two octaves by repeating its three-note group
  (`two_octaves()`), with no new thumbs on black keys.
- In root-position arpeggios, the left hand puts 3 on the chord's 3rd only when it's a major
  3rd on a black key (D, A, E, B, F♯ major) and 4 everywhere else, as the note on page 5 says.
- The harmonic minor form keeps the thumbs off black keys. The melodic minor exceptions on
  page 3 are exactly the keys where the raised 6th or 7th would put a thumb on a black key.
- In chords, notes a step apart get neighbouring fingers. Chord-type notes match their
  formulas, and the "all notes" / "no 3rd" labels on extended voicings are true.
- `auto_fingering()` reproduces every major and minor scale fingering on the sheet (the right
  hand's very first finger excepted: B♭ minor may start on 2 or 4).
- Every mode and jazz scale really is the stated mode of its parent scale (major, melodic or
  harmonic minor), its degree formula matches its notes, and its generated fingering passes
  the thumb and finger-order checks.
- The pentatonic, blues and symmetric scales match their step patterns and formulas.
- The faster chromatic fingering covers one octave of half steps and puts the thumb only on
  E, G, B and D.
- Every chord type's piano shape fits its size: three-note chords use triad or sus shapes,
  four-note chords the four-note, 6th or add9 shapes, five-note chords two hands.

## Sources

- Scale and chord fingerings: common teaching practice, as used by exam boards such as ABRSM.
- Arpeggios: Robert Kelley, [Piano Arpeggio Fingerings](https://robertkelleyphd.com/home/arpfing.htm).
- Melodic minor exceptions: Greg Spero, [melodic minor fingering lesson](https://composition.gregspero.com/lessons/a3/).
- Faster chromatic fingering (RH, from E: 1 2 3 1 2 3 4 1 2 3 1 2): Chuan C. Chang,
  [Fundamentals of Piano Practice, "Fast Chromatic Scales"](https://fundamentals-of-piano-practice.readthedocs.io/chapter1/ch1_topics/III.5.html),
  which attributes it to Hauer, Czerny and Hanon.

Other good fingerings exist, and hand size matters.
