"""The piano fingering sheet: scales, chord shapes, arpeggios and chord/scale reference tables.

A sheet module provides SLUG, TITLE, NAME, PAGES, validate() and summary(); build.py renders it.
"""
from music import black_pc, is_black, pc, steps
from parts import acc, cell, cells, digit, key_label

SLUG = "piano-fingering"           # output file names: dist/piano-fingering.pdf, .html
TITLE = "Piano Fingering Sheet"    # page title (browser tab, artifact gallery)
NAME = "Piano Fingering"           # running head on printed pages, name on the site index
DESCRIPTION = ("Every major and minor scale, modes and jazz scales, chord shapes and arpeggios, "
               "with fingering for both hands.")

errors = []


def err(msg):
    errors.append(msg)


def fing(s):
    return [int(c) for c in s.replace(" ", "")]


def check_letters(name, ns):
    order = "CDEFGAB"
    for a, b in zip(ns, ns[1:]):
        if (order.index(a[0]) + 1) % 7 != order.index(b[0]):
            err(f"{name}: letters not consecutive {a}->{b}")


def check_moves(name, hand, f_up):
    """f_up: fingers in ascending pitch order."""
    for a, b in zip(f_up, f_up[1:]):
        if hand == "RH":
            ok = b > a or (b == 1 and a in (2, 3, 4))
        else:
            ok = b < a or (a == 1 and b in (2, 3, 4))
        if not ok:
            err(f"{name} {hand}: awkward move {a}->{b} in {f_up}")


def check_thumbs(name, hand, ns, f):
    for n, x in zip(ns, f):
        if x == 1 and is_black(n):
            err(f"{name} {hand}: thumb on black key {n}")


# ---------------------------------------------------------------- data
# Major scales, circle-of-fifths order. (key, other name, key signature, notes, RH, LH)
MAJOR = [
    ("C", "", "no ♯ or ♭", "C D E F G A B C", "12312345", "54321321"),
    ("G", "", "1♯", "G A B C D E F♯ G", "12312345", "54321321"),
    ("D", "", "2♯", "D E F♯ G A B C♯ D", "12312345", "54321321"),
    ("A", "", "3♯", "A B C♯ D E F♯ G♯ A", "12312345", "54321321"),
    ("E", "", "4♯", "E F♯ G♯ A B C♯ D♯ E", "12312345", "54321321"),
    ("B", "C♭", "5♯", "B C♯ D♯ E F♯ G♯ A♯ B", "12312345", "43214321"),
    ("F♯", "G♭", "6♯", "F♯ G♯ A♯ B C♯ D♯ E♯ F♯", "23412312", "43213214"),
    ("D♭", "C♯", "5♭", "D♭ E♭ F G♭ A♭ B♭ C D♭", "23123412", "32143213"),
    ("A♭", "", "4♭", "A♭ B♭ C D♭ E♭ F G A♭", "34123123", "32143213"),
    ("E♭", "", "3♭", "E♭ F G A♭ B♭ C D E♭", "31234123", "32143213"),
    ("B♭", "", "2♭", "B♭ C D E♭ F G A B♭", "41231234", "32143213"),
    ("F", "", "1♭", "F G A B♭ C D E F", "12341234", "54321321"),
]
MAJOR_GROUPS = [5, 1, 2, 4]  # C–E | B | F♯ D♭ | flat keys

# Minor scales (natural minor notes; harmonic raises the 7th, same fingers).
# (key, other name, relative major, key signature, notes, RH, LH)
MINOR = [
    ("A", "", "C", "no ♯ or ♭", "A B C D E F G A", "12312345", "54321321"),
    ("E", "", "G", "1♯", "E F♯ G A B C D E", "12312345", "54321321"),
    ("B", "", "D", "2♯", "B C♯ D E F♯ G A B", "12312345", "43214321"),
    ("F♯", "", "A", "3♯", "F♯ G♯ A B C♯ D E F♯", "34123123", "43213214"),
    ("C♯", "", "E", "4♯", "C♯ D♯ E F♯ G♯ A B C♯", "34123123", "32143213"),
    ("G♯", "A♭", "B", "5♯", "G♯ A♯ B C♯ D♯ E F♯ G♯", "34123123", "32132143"),
    ("E♭", "D♯", "G♭", "6♭", "E♭ F G♭ A♭ B♭ C♭ D♭ E♭", "31234123", "21432132"),
    ("B♭", "A♯", "D♭", "5♭", "B♭ C D♭ E♭ F G♭ A♭ B♭", "21231234", "21321432"),
    ("F", "", "A♭", "4♭", "F G A♭ B♭ C D♭ E♭ F", "12341234", "54321321"),
    ("C", "", "E♭", "3♭", "C D E♭ F G A♭ B♭ C", "12312345", "54321321"),
    ("G", "", "B♭", "2♭", "G A B♭ C D E♭ F G", "12312345", "54321321"),
    ("D", "", "F", "1♭", "D E F G A B♭ C D", "12312345", "54321321"),
]
MINOR_GROUPS = [3, 3, 2, 4]  # A E B | F♯ C♯ G♯ | E♭ B♭ | F C G D

# Melodic minor: only these two keys change (right hand). Up = raised 6th & 7th, down = natural.
MELODIC = [
    ("F♯", "F♯ G♯ A B C♯ D♯ E♯ F♯", "23123412", "F♯ E D C♯ B A G♯ F♯", "21321432"),
    ("C♯", "C♯ D♯ E F♯ G♯ A♯ B♯ C♯", "34123412", "C♯ B A G♯ F♯ E D♯ C♯", "21432132"),
]

CHROMATIC = ("C C♯ D D♯ E F F♯ G G♯ A A♯ B C", "1313123131312", "1313213131321")
# Faster right-hand chromatic fingering in groups of 1 2 3 and 1 2 3 4, thumb only on E, G, B, D.
# Chuan C. Chang, Fundamentals of Piano Practice, after Hauer, Czerny and Hanon.
CHROMATIC_FAST = ("E F F♯ G G♯ A A♯ B C C♯ D D♯ E", "1231234123121")

STEP = {"H": 1, "W": 2, "W+H": 3}

# Modes and other seven-note scales, all on C so they can be compared.
# (name, where it comes from, notes, formula vs major, sound, (parent scale, mode number))
# Their fingerings are not hand-written: auto_fingering() works them out with the same rules
# that reproduce every standard major and minor fingering above (checked in validate()).
PARENTS = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "melodic minor": [2, 1, 2, 2, 2, 2, 1],
    "harmonic minor": [2, 1, 2, 2, 1, 3, 1],
}
# In mode order, i.e. by the white key each one starts on (C, D, E, F, G, A, B).
MODES = [
    ("Ionian (major)", "white keys C to C", "C D E F G A B C", "1 2 3 4 5 6 7", "the major scale", ("major", 1)),
    ("Dorian", "white keys D to D", "C D E♭ F G A B♭ C", "1 2 ♭3 4 5 6 ♭7", "minor with a brighter 6th", ("major", 2)),
    ("Phrygian", "white keys E to E", "C D♭ E♭ F G A♭ B♭ C", "1 ♭2 ♭3 4 5 ♭6 ♭7", "dark, Spanish-sounding", ("major", 3)),
    ("Lydian", "white keys F to F", "C D E F♯ G A B C", "1 2 3 ♯4 5 6 7", "bright, floating", ("major", 4)),
    ("Mixolydian", "white keys G to G", "C D E F G A B♭ C", "1 2 3 4 5 6 ♭7", "major with a bluesy 7th", ("major", 5)),
    ("Aeolian (natural minor)", "white keys A to A", "C D E♭ F G A♭ B♭ C", "1 2 ♭3 4 5 ♭6 ♭7", "the natural minor scale", ("major", 6)),
    ("Locrian", "white keys B to B", "C D♭ E♭ F G♭ A♭ B♭ C", "1 ♭2 ♭3 4 ♭5 ♭6 ♭7", "unstable: the 5th is diminished", ("major", 7)),
]
JAZZ_SCALES = [
    ("Melodic minor", "jazz minor: same going down", "C D E♭ F G A B C", "1 2 ♭3 4 5 6 7", "minor with a major 6th and 7th", ("melodic minor", 1)),
    ("Lydian dominant", "mode 4 of melodic minor", "C D E F♯ G A B♭ C", "1 2 3 ♯4 5 6 ♭7", "over 7♯11 chords", ("melodic minor", 4)),
    ("Mixolydian ♭6", "mode 5 of melodic minor", "C D E F G A♭ B♭ C", "1 2 3 4 5 ♭6 ♭7", "dominant with a darker 6th", ("melodic minor", 5)),
    ("Locrian ♮2", "mode 6 of melodic minor", "C D E♭ F G♭ A♭ B♭ C", "1 2 ♭3 4 ♭5 ♭6 ♭7", "over m7♭5 (half-diminished) chords", ("melodic minor", 6)),
    ("Altered", "mode 7 of melodic minor", "C D♭ D♯ E G♭ A♭ B♭ C", "1 ♭9 ♯9 3 ♭5 ♭13 ♭7", "over altered dominant (7alt) chords", ("melodic minor", 7)),
    ("Phrygian dominant", "mode 5 of harmonic minor", "C D♭ E F G A♭ B♭ C", "1 ♭2 3 4 5 ♭6 ♭7", "flamenco, Middle Eastern, metal", ("harmonic minor", 5)),
]
# Scales without a standard fingering: notes and how they differ from major only.
# (name, notes, formula vs major, steps, sound)
MORE_SCALES = [
    ("Major pentatonic", "C D E G A C", "1 2 3 5 6", "W W W+H W W+H", "major without 4 and 7"),
    ("Minor pentatonic", "C E♭ F G B♭ C", "1 ♭3 4 5 ♭7", "W+H W W W+H W", "rock and blues solos"),
    ("Blues", "C E♭ F G♭ G B♭ C", "1 ♭3 4 ♭5 5 ♭7", "W+H W H H W+H W", "minor pentatonic plus ♭5"),
    ("Whole-tone", "C D E F♯ G♯ B♭ C", "1 2 3 ♯4 ♯5 ♭7", "W W W W W W", "dreamy, no home note"),
    ("Diminished, half-whole", "C D♭ E♭ E F♯ G A B♭ C", "1 ♭9 ♯9 3 ♯11 5 13 ♭7", "H W H W H W H W", "over 7♭9 chords"),
    ("Diminished, whole-half", "C D E♭ F G♭ A♭ A B C", "1 2 ♭3 4 ♭5 ♭6 6 7", "W H W H W H W H", "over diminished 7th chords"),
]
SCALE_DEG = {"1": 0, "♭2": 1, "♭9": 1, "2": 2, "9": 2, "♭3": 3, "♯9": 3, "3": 4, "4": 5, "♯4": 6,
             "♯11": 6, "♭5": 6, "5": 7, "♯5": 8, "♭6": 8, "♭13": 8, "6": 9, "13": 9, "♭7": 10, "7": 11}

# Fingering rules for seven-note scales. Each octave is one group of three fingers and one of
# four, so the fingers going up are a rotation of these cycles (the thumb starts each group).
RH_CYCLE = [1, 2, 3, 1, 2, 3, 4]
LH_CYCLE = [4, 3, 2, 1, 3, 2, 1]


def auto_fingering(ns):
    """Fingering for a seven-note scale (8 notes including the octave), both hands, going up.

    Rules, in order: the thumb never plays a black key; if the scale starts on a white key, start
    on the thumb; put the thumb right after a black key (RH) or right before one (LH) as often as
    possible; then prefer the group of three first (RH) or the group of four first (LH). The
    outer note gets 5 (or 4) when the hand starts or ends there.
    """
    body = ns[:7]
    black = [is_black(n) for n in body]
    tonic_white = not black[0]

    def best(cycle, score, tie):
        options = []
        for r in range(7):
            f = [cycle[(r + i) % 7] for i in range(8)]
            if any(f[i] == 1 and black[i] for i in range(7)):
                continue
            options.append(((tonic_white and f[0] == 1, score(f), tie(f)), f))
        return max(options)[1]

    rh = best(RH_CYCLE,
              lambda f: sum(1 for i in range(7) if f[i] == 1 and black[(i - 1) % 7]),
              lambda f: f[:4] == [1, 2, 3, 1])
    lh = best(LH_CYCLE,
              lambda f: sum(1 for i in range(7) if f[i] == 1 and black[(i + 1) % 7]),
              lambda f: f[:5] == [1, 4, 3, 2, 1])
    rh, lh = rh[:], lh[:]
    if rh[7] == 1:          # top of the right hand: 5 (or 4) instead of the thumb
        rh[7] = rh[6] + 1
    if lh[0] == 1:          # bottom of the left hand: 5 (or 4) instead of the thumb
        lh[0] = lh[1] + 1
    return rh, lh

# Block chords (close position, C examples). (title, hint, notes, RH, LH)
CHORD_CARDS = [
    ("Triads", [
        ("Root position", "root at the bottom", "C E G", "135", "531"),
        ("1st inversion", "3rd at the bottom", "E G C", "125", "531"),
        ("2nd inversion", "5th at the bottom", "G C E", "135", "521"),
    ]),
    ("Four-note chords (every kind of 7th chord)", [
        ("Root position", "Cmaj7", "C E G B", "1235", "5321"),
        ("1st inversion", "3rd at the bottom", "E G B C", "1245", "5321"),
        ("2nd inversion", "5th at the bottom", "G B C E", "1235", "5321"),
        ("3rd inversion", "7th at the bottom", "B C E G", "1235", "5421"),
    ]),
    ("Other shapes", [
        ("sus2", "Csus2", "C D G", "125", "541"),
        ("sus4", "Csus4", "C F G", "145", "521"),
        ("add9, close", "Cadd9", "C D E G", "1235", "5431"),
        ("6th chord", "C6", "C E G A", "1245", "5321"),
    ]),
]

# Chord types. (name, symbol, formula, notes in C, how to finger)
CHORD_TYPES = [
    ("Major", "C", "1 3 5", "C E G", "Triad"),
    ("Minor", "Cm", "1 ♭3 5", "C E♭ G", "Triad"),
    ("Diminished", "Cdim, C°", "1 ♭3 ♭5", "C E♭ G♭", "Triad"),
    ("Augmented", "Caug, C+", "1 3 ♯5", "C E G♯", "Triad"),
    ("Suspended 2nd", "Csus2", "1 2 5", "C D G", "sus2"),
    ("Suspended 4th", "Csus4", "1 4 5", "C F G", "sus4"),
    ("Sixth", "C6", "1 3 5 6", "C E G A", "6th chord"),
    ("Minor sixth", "Cm6", "1 ♭3 5 6", "C E♭ G A", "6th chord"),
    ("Added ninth", "Cadd9", "1 3 5 9", "C E G D", "add9"),
    ("Major seventh", "Cmaj7", "1 3 5 7", "C E G B", "Four-note"),
    ("Dominant seventh", "C7", "1 3 5 ♭7", "C E G B♭", "Four-note"),
    ("Minor seventh", "Cm7", "1 ♭3 5 ♭7", "C E♭ G B♭", "Four-note"),
    ("Half-diminished", "Cm7♭5, Cø", "1 ♭3 ♭5 ♭7", "C E♭ G♭ B♭", "Four-note"),
    ("Diminished seventh", "Cdim7, C°7", "1 ♭3 ♭5 ♭♭7", "C E♭ G♭ A", "Four-note"),
    ("Minor-major seventh", "Cm(maj7)", "1 ♭3 5 7", "C E♭ G B", "Four-note"),
    ("Seventh sus4", "C7sus4", "1 4 5 ♭7", "C F G B♭", "Four-note"),
    ("Ninth", "C9", "1 3 5 ♭7 9", "C E G B♭ D", "Two hands"),
    ("Major ninth", "Cmaj9", "1 3 5 7 9", "C E G B D", "Two hands"),
    ("Minor ninth", "Cm9", "1 ♭3 5 ♭7 9", "C E♭ G B♭ D", "Two hands"),
    ("Six-nine", "C6/9", "1 3 5 6 9", "C E G A D", "Two hands"),
    ("Eleventh", "C11", "1 5 ♭7 9 11", "C G B♭ D F", "Two hands"),
    ("Thirteenth", "C13", "1 3 ♭7 9 13", "C E B♭ D A", "Two hands"),
]
DEG = {"1": 0, "♭2": 1, "2": 2, "♭3": 3, "3": 4, "4": 5, "♭5": 6, "5": 7, "♯5": 8,
       "6": 9, "♭♭7": 9, "♭7": 10, "7": 11, "9": 2, "11": 5, "13": 9}

# Extended chords split between the hands. (symbol, LH notes, LH fingers, RH notes, RH fingers, note)
EXTENDED = [
    ("Cmaj9", "C G", "51", "E G B D", "1235", "all notes"),
    ("C9", "C B♭", "51", "E G D", "125", "all notes"),
    ("Cm9", "C B♭", "51", "E♭ G D", "125", "all notes"),
    ("C6/9", "C G", "51", "E A D", "135", "all notes"),
    ("C11", "C G", "51", "B♭ D F", "135", "no 3rd"),
    ("C13", "C B♭", "51", "E A D", "135", "no 5th, 11th"),
]
EXT_MISSING = {"C11": {"E"}, "C13": {"G", "F"}}

# Arpeggios, root position, one octave. After Robert Kelley's standard arpeggio chart.
ARP_MAJOR = [
    ("C", "", "C E G C", "1235", "5421"),
    ("G", "", "G B D G", "1235", "5421"),
    ("D", "", "D F♯ A D", "1235", "5321"),
    ("A", "", "A C♯ E A", "1235", "5321"),
    ("E", "", "E G♯ B E", "1235", "5321"),
    ("B", "", "B D♯ F♯ B", "1235", "5321"),
    ("F♯", "G♭", "F♯ A♯ C♯ F♯", "1235", "5321"),
    ("D♭", "C♯", "D♭ F A♭ D♭", "2124", "2142"),
    ("A♭", "", "A♭ C E♭ A♭", "2124", "2142"),
    ("E♭", "", "E♭ G B♭ E♭", "2124", "2142"),
    ("B♭", "", "B♭ D F B♭", "2124", "3213"),
    ("F", "", "F A C F", "1235", "5421"),
]
ARP_MINOR = [
    ("A", "", "A C E A", "1235", "5421"),
    ("E", "", "E G B E", "1235", "5421"),
    ("B", "", "B D F♯ B", "1235", "5421"),
    ("F♯", "", "F♯ A C♯ F♯", "2124", "2142"),
    ("C♯", "", "C♯ E G♯ C♯", "2124", "2142"),
    ("G♯", "A♭", "G♯ B D♯ G♯", "2124", "2142"),
    ("E♭", "D♯", "E♭ G♭ B♭ E♭", "1235", "5421"),
    ("B♭", "A♯", "B♭ D♭ F B♭", "2312", "3213"),
    ("F", "", "F A♭ C F", "1235", "5421"),
    ("C", "", "C E♭ G C", "1235", "5421"),
    ("G", "", "G B♭ D G", "1235", "5421"),
    ("D", "", "D F A D", "1235", "5421"),
]
ARP_INV = [
    ("Root position", "C E G C", "1235", "5421"),
    ("1st inversion", "E G C E", "1245", "5421"),
    ("2nd inversion", "G C E G", "1245", "5321"),
]
# Arpeggios written out over two octaves on the sheet: (key, "major" or "minor").
ARP_EXAMPLES = [("C", "major"), ("G♯", "minor")]


def two_octaves(f, hand):
    """Extend a one-octave arpeggio fingering to two octaves; the pattern repeats every three notes.

    C major RH 1 2 3 5 -> 1 2 3 1 2 3 5 (the top 5 becomes the thumb when you carry on).
    G♯ minor RH 2 1 2 4 -> 2 1 2 4 1 2 4 (only the first note's finger is special).
    """
    a, b, c, d = f
    if hand == "RH" and d == 5:
        return [a, b, c, a, b, c, 5]
    return [a, b, c, d, b, c, d]


def lh_three_keys():
    """Major arpeggios whose left hand uses 3 on the 3rd (a major 3rd on a black key), as HTML."""
    keys = [key for key, _, notes, _, lh in ARP_MAJOR
            if fing(lh)[0] == 5 and is_black(notes.split()[1])]
    return ", ".join(acc(k) for k in keys)


def repeat_text(f2, hand):
    if hand == "RH" and f2[-1] == 5 and f2[0] == f2[3]:
        return f"{f2[0]} {f2[1]} {f2[2]} repeats, 5 at the top"
    return f"{f2[0]}, then {f2[1]} {f2[2]} {f2[3]} repeats"


# ---------------------------------------------------------------- validation
def validate():
    """Check every scale, chord and arpeggio on the sheet. Returns a list of problems."""
    errors.clear()
    for key, _, _, notes, rh, lh in MAJOR:
        ns, r, l = notes.split(), fing(rh), fing(lh)
        name = f"{key} major"
        if steps(ns) != [2, 2, 1, 2, 2, 2, 1]:
            err(f"{name}: wrong notes {ns}")
        check_letters(name, ns)
        for hand, f in (("RH", r), ("LH", l)):
            if len(f) != 8:
                err(f"{name} {hand}: needs 8 fingers")
            check_thumbs(name, hand, ns, f)
            check_moves(name, hand, f)

    melodic_problems = set()
    for key, _, rel, _, notes, rh, lh in MINOR:
        ns, r, l = notes.split(), fing(rh), fing(lh)
        name = f"{key} minor"
        if steps(ns) != [2, 1, 2, 2, 1, 2, 2]:
            err(f"{name}: wrong natural-minor notes {ns}")
        check_letters(name, ns)
        if pc(rel) != (pc(ns[0]) + 3) % 12:
            err(f"{name}: wrong relative major {rel}")
        pcs = [pc(n) for n in ns]
        harmonic = pcs[:6] + [pcs[6] + 1, pcs[7]]
        melodic = pcs[:5] + [pcs[5] + 1, pcs[6] + 1, pcs[7]]
        for hand, f in (("RH", r), ("LH", l)):
            if len(f) != 8:
                err(f"{name} {hand}: needs 8 fingers")
            check_thumbs(name, hand, ns, f)
            check_moves(name, hand, f)
            for p, x in zip(harmonic, f):
                if x == 1 and black_pc(p):
                    err(f"{name} {hand}: harmonic form puts thumb on a black key")
            for p, x in zip(melodic, f):
                if x == 1 and black_pc(p):
                    melodic_problems.add((key, hand))

    expected_melodic = {(k, "RH") for k, *_ in MELODIC}
    if melodic_problems != expected_melodic:
        err(f"melodic exceptions mismatch: found {sorted(melodic_problems)}, sheet lists {sorted(expected_melodic)}")

    for key, up, rh_up, down, rh_down in MELODIC:
        name = f"{key} melodic minor"
        u, d = up.split(), down.split()
        if steps(u) != [2, 1, 2, 2, 2, 2, 1]:
            err(f"{name}: wrong ascending notes")
        if steps(list(reversed(d))) != [2, 1, 2, 2, 1, 2, 2]:
            err(f"{name}: wrong descending notes")
        if u[0] != d[0] and pc(u[0]) != pc(d[0]):
            err(f"{name}: start mismatch")
        check_thumbs(name + " up", "RH", u, fing(rh_up))
        check_moves(name + " up", "RH", fing(rh_up))
        check_thumbs(name + " down", "RH", d, fing(rh_down))
        check_moves(name + " down", "RH", list(reversed(fing(rh_down))))
        if fing(rh_up)[-1] != fing(rh_down)[0]:
            err(f"{name}: top finger differs between up and down")

    cn = CHROMATIC[0].split()
    if steps(cn) != [1] * 12:
        err("chromatic notes wrong")
    for hand, f in (("RH", fing(CHROMATIC[1])), ("LH", fing(CHROMATIC[2]))):
        check_moves("chromatic", hand, f)
        for n, x in zip(cn, f):
            if is_black(n) and x != 3:
                err(f"chromatic {hand}: black key {n} should be 3")
    fast_notes, fast = CHROMATIC_FAST[0].split(), fing(CHROMATIC_FAST[1])
    if steps(fast_notes) != [1] * 12 or len(fast) != 13:
        err("fast chromatic: notes must be one octave of half steps")
    check_thumbs("fast chromatic", "RH", fast_notes, fast)
    check_moves("fast chromatic", "RH", fast)
    if sorted({n for n, x in zip(fast_notes, fast) if x == 1}) != ["B", "D", "E", "G"]:
        err("fast chromatic: thumb should land only on E, G, B and D")

    # The fingering rules must reproduce every hand-written major and minor fingering
    # (the right hand's very first finger may differ: B♭ minor starts on 2 or 4).
    for label, rows in (("major", [(k, n, r, l) for k, _, _, n, r, l in MAJOR]),
                        ("minor", [(k, n, r, l) for k, _, _, _, n, r, l in MINOR])):
        for key, notes, rh, lh in rows:
            auto_r, auto_l = auto_fingering(notes.split())
            if auto_r[1:] != fing(rh)[1:] or auto_l != fing(lh):
                err(f"fingering rules don't reproduce {key} {label}: {auto_r} {auto_l}")

    if [mode for *_, (_, mode) in MODES] != list(range(1, 8)):
        err("modes must be listed in mode order (Ionian, Dorian, Phrygian, ...)")
    for name, source, notes, formula, _, (parent, mode) in MODES + JAZZ_SCALES:
        ns = notes.split()
        if steps(ns) != PARENTS[parent][mode - 1:] + PARENTS[parent][:mode - 1]:
            err(f"{name}: notes are not mode {mode} of {parent}")
        if parent == "major" and source != f"white keys {'CDEFGAB'[mode - 1]} to {'CDEFGAB'[mode - 1]}":
            err(f"{name}: wrong white-key start '{source}'")
        if [SCALE_DEG[d] for d in formula.split()] != [(pc(n) - pc("C")) % 12 for n in ns[:7]]:
            err(f"{name}: formula {formula} doesn't match notes")
        rh, lh = auto_fingering(ns)
        for hand, f in (("RH", rh), ("LH", lh)):
            check_thumbs(name, hand, ns, f)
            check_moves(name, hand, f)

    for name, notes, formula, st, _ in MORE_SCALES:
        ns = notes.split()
        want = [STEP[s] for s in st.split()]
        if steps(ns) != want or sum(want) != 12:
            err(f"{name}: steps {st} don't match notes {ns}")
        if [SCALE_DEG[d] for d in formula.split()] != [(pc(n) - pc("C")) % 12 for n in ns[:-1]]:
            err(f"{name}: formula {formula} doesn't match notes")

    for _, cards in CHORD_CARDS:
        for title, hint, notes, rh, lh in cards:
            ns, r, l = notes.split(), fing(rh), fing(lh)
            name = f"chord {title} {notes}"
            absp, last = [], -1
            for n in ns:
                p = pc(n)
                while p <= last:
                    p += 12
                absp.append(p)
                last = p
            if absp[-1] - absp[0] > 9 + 2:
                err(f"{name}: span too wide for close position")
            if r[0] != 1 or l[-1] != 1:
                err(f"{name}: thumbs must be RH bottom / LH top")
            if any(b <= a for a, b in zip(r, r[1:])) or any(b >= a for a, b in zip(l, l[1:])):
                err(f"{name}: fingers must run in order")
            for i in range(len(ns) - 1):
                if absp[i + 1] - absp[i] <= 2:
                    if r[i + 1] - r[i] != 1 or l[i] - l[i + 1] != 1:
                        err(f"{name}: notes a step apart need neighbouring fingers")

    shapes = {3: {"Triad", "sus2", "sus4"}, 4: {"Four-note", "6th chord", "add9"}, 5: {"Two hands"}}
    for name, sym, formula, notes, how in CHORD_TYPES:
        want = sorted({DEG[d] for d in formula.split()})
        got = sorted({(pc(n) - pc("C")) % 12 for n in notes.split()})
        if want != got:
            err(f"{sym}: formula {formula} vs notes {notes}")
        if how not in shapes.get(len(notes.split()), set()):
            err(f"{sym}: piano shape {how!r} doesn't fit a {len(notes.split())}-note chord")

    ext_full = {sym: notes for _, sym, _, notes, _ in CHORD_TYPES}
    ext_full["C11"] = "C E G B♭ D F"
    ext_full["C13"] = "C E G B♭ D F A"
    for sym, ln, lf, rn, rf, _ in EXTENDED:
        tones = {pc(n) for n in ext_full[sym].split()}
        used = {pc(n) for n in (ln + " " + rn).split()}
        if not used <= tones:
            err(f"{sym}: voicing uses a note outside the chord")
        missing = {n for n in ext_full[sym].split() if pc(n) not in used}
        if missing != EXT_MISSING.get(sym, set()):
            err(f"{sym}: voicing leaves out {missing}, label says {EXT_MISSING.get(sym, set())}")
        if pc(ln.split()[0]) != pc("C"):
            err(f"{sym}: LH must start on the root")
        if len(lf) != len(ln.split()) or len(rf) != len(rn.split()):
            err(f"{sym}: finger count mismatch")

    def check_arp(name, notes, rh, lh, quality):
        ns, r, l = notes.split(), fing(rh), fing(lh)
        want = [4, 3, 5] if quality == "major" else [3, 4, 5]
        if steps(ns) != want:
            err(f"{name}: wrong notes {ns}")
        all_black = all(is_black(n) for n in ns)
        ns2 = ns + ns[1:]
        for hand, f in (("RH", r), ("LH", l)):
            check_moves(name, hand, f)
            f2 = two_octaves(f, hand)
            check_moves(name + " (two octaves)", hand, f2)
            if not all_black:
                check_thumbs(name, hand, ns, f)
                check_thumbs(name + " (two octaves)", hand, ns2, f2)

    for key, _, notes, rh, lh in ARP_MAJOR:
        check_arp(f"{key} major arpeggio", notes, rh, lh, "major")
    for key, _, notes, rh, lh in ARP_MINOR:
        check_arp(f"{key} minor arpeggio", notes, rh, lh, "minor")

    # The note on the arpeggio page: in root position the left hand puts 3 on the chord's 3rd
    # only when it's a major 3rd on a black key; otherwise 4.
    for quality, table in (("major", ARP_MAJOR), ("minor", ARP_MINOR)):
        for key, _, notes, rh, lh in table:
            l = fing(lh)
            if l[0] != 5:
                continue
            third = notes.split()[1]
            want = 3 if quality == "major" and is_black(third) else 4
            if l[1] != want:
                err(f"{key} {quality} arpeggio LH: 3rd ({third}) should take {want}")
    for title, notes, rh, lh in ARP_INV:
        check_moves(f"C inversion {title}", "RH", fing(rh))
        check_moves(f"C inversion {title}", "LH", fing(lh))
    return list(errors)


def summary():
    return (f"{len(MAJOR)} major, {len(MINOR)} minor, {len(MELODIC)} melodic exceptions, "
            f"{len(MODES) + len(JAZZ_SCALES)} modes and jazz scales, {len(MORE_SCALES)} more scales, "
            f"{len(ARP_MAJOR) + len(ARP_MINOR)} arpeggios, "
            f"{sum(len(c) for _, c in CHORD_CARDS)} chord shapes, {len(CHORD_TYPES)} chord types")


# ---------------------------------------------------------------- HTML helpers
def fourth(ns, f):
    mid = [ns[i] for i in range(1, 7) if f[i] == 4]
    if not mid:
        mid = [ns[i] for i in (0, 7) if f[i] == 4]
    seen = []
    for n in mid:
        if n not in seen:
            seen.append(n)
    return " ".join(seen)


def scale_row(key, small, ns, r, l, alt=False):
    return (
        f'<div class="srow{" alt" if alt else ""}">'
        + key_label(key, small)
        + cells(ns, r, l)
        + '<div class="four">'
        + f'<span><i class="rh">RH</i> {acc(fourth(ns, r))}</span>'
        + f'<span><i class="lh">LH</i> {acc(fourth(ns, l))}</span>'
        + "</div></div>"
    )


def grouped(rows, groups):
    out, i = [], 0
    for g in groups:
        out.append('<div class="grp">' + "".join(rows[i:i + g]) + "</div>")
        i += g
    return "".join(out)


def table_head(first, last):
    return (
        '<div class="shead">'
        f"<span>{first}</span>"
        '<span><i class="rh">Right hand</i> above · note · <i class="lh">left hand</i> below, going up</span>'
        f"<span>{last}</span>"
        "</div>"
    )


# ---------------------------------------------------------------- sections
# Each section is a self-contained block; PAGES below decides which go on which A4 page.
def sec_header():
    return f"""
  <header class="top">
    <div class="title">
      <h1>Piano Fingering</h1>
      <p class="sub">Scales, chords and arpeggios. One octave, hands separately, every key.</p>
    </div>
    <div class="legend">
      <div class="legend-l">
        <div class="fingers">
          <span><b>1</b> thumb</span><span><b>2</b> index</span><span><b>3</b> middle</span><span><b>4</b> ring</span><span><b>5</b> little</span>
        </div>
        <div class="thumbnote">{digit(1, "rh")}{digit(1, "lh")}<span>circled number = thumb</span></div>
      </div>
      <div class="howto">
        {cell("E♭", 3, 2)}
        <div class="howto-t">
          <span><i class="rh">Blue</i> right-hand finger</span>
          <span>White or black key</span>
          <span><i class="lh">Red</i> left-hand finger</span>
        </div>
      </div>
    </div>
  </header>

  <div class="notes2">
    <div>
      <h4>Reading the rows</h4>
      <ul>
        <li>Fingers are written going up. Coming down, play the same fingers in reverse.</li>
        <li>For two or more octaves, repeat the pattern. Only the very first and last notes may change finger (a 5 becomes the thumb).</li>
        <li>The thumb never lands on a black key in any scale on this sheet.</li>
      </ul>
    </div>
    <div>
      <h4>Patterns worth memorising</h4>
      <ul>
        <li>C, G, D, A and E major all use the same fingers.</li>
        <li>Each hand uses finger 4 once per octave. Learn that note (Finger 4 column) and the rest falls into place.</li>
        <li>In every flat major key, right-hand 4 plays B<span class="acc">♭</span>.</li>
      </ul>
    </div>
  </div>
"""


def sec_major():
    rows = [scale_row(key, (f"= {other} · " if other else "") + sig, notes.split(), fing(rh), fing(lh),
                      alt=i % 2 == 1)
            for i, (key, other, sig, notes, rh, lh) in enumerate(MAJOR)]
    return f"""
  <h2>Major scales</h2>
  {table_head("Key", "Finger 4")}
  {grouped(rows, MAJOR_GROUPS)}
"""


def sec_minor():
    rows = [scale_row(key, (f"= {other} · " if other else "") + f"rel. {rel} · {sig}", notes.split(),
                      fing(rh), fing(lh), alt=i % 2 == 1)
            for i, (key, other, rel, sig, notes, rh, lh) in enumerate(MINOR)]
    return f"""
  <h2>Minor scales</h2>
  <p class="lead">Natural minor shown. <b>Harmonic minor</b> raises the 7th note (the one before the top) a half step (A minor: G becomes G<span class="acc">♯</span>) and keeps the same fingers in every key.</p>
  {table_head("Key", "Finger 4")}
  {grouped(rows, MINOR_GROUPS)}
"""


def sec_melodic():
    melodic_html = ""
    for key, up, rh_up, down, rh_down in MELODIC:
        melodic_html += (
            '<div class="mel">'
            f'<div class="mel-k">{acc(key)} melodic minor, right hand</div>'
            '<div class="mel-r"><span class="dir">up</span>'
            + cells(up.split(), fing(rh_up), rows="rh")
            + '</div><div class="mel-r"><span class="dir">down</span>'
            + cells(down.split(), fing(rh_down), rows="rh")
            + "</div></div>"
        )
    return f"""
  <h2>Melodic minor</h2>
  <p class="lead">Going up, raise the 6th and 7th. Coming down, play the natural minor. The minor-scale fingers still work in every key except these two, where the raised 6th would put the right thumb on a black key. The left hand doesn't change.</p>
  <div class="mels">{melodic_html}</div>
"""


def sec_chromatic():
    chrom = cells(CHROMATIC[0].split(), fing(CHROMATIC[1]), fing(CHROMATIC[2]))
    fast = cells(CHROMATIC_FAST[0].split(), fing(CHROMATIC_FAST[1]), rows="rh")
    return f"""
  <h2>Chromatic scale</h2>
  <p class="lead"><b>Standard:</b> 3 on every black key, thumb on white keys. Where two white keys meet, use 2: right hand on F and C, left hand on E and B (going up). Works from any starting note.</p>
  <div class="chrom">{chrom}</div>
  <p class="lead"><b>Faster, right hand:</b> groups of 1 2 3 and 1 2 3 4 with the thumb only on E, G, B and D, the same every octave. Fewer thumb crossings make it smoother at speed (after Czerny and Hanon).</p>
  <div class="chrom">{fast}</div>
"""


def formula_html(formula):
    """Scale degrees, with the ones that differ from major in bold."""
    return " ".join(f"<b>{acc(d)}</b>" if d[0] in "♭♯" else acc(d) for d in formula.split())


def mode_rows(scales):
    rows = []
    for i, (name, source, notes, formula, sound, _) in enumerate(scales):
        ns = notes.split()
        rh, lh = auto_fingering(ns)
        rows.append(
            f'<div class="mrow{" alt" if i % 2 else ""}">'
            f'<div class="mname"><b>{acc(name)}</b><span class="formula">{formula_html(formula)}</span>'
            f'<small>{acc(source)}</small></div>'
            + cells(ns, rh, lh)
            + f'<div class="msound">{acc(sound)}</div></div>'
        )
    return "".join(rows)


def white_key_modes():
    """The seven white keys, each labelled with the mode you get playing white keys from it."""
    items = ""
    for name, _, _, _, _, (_, mode) in MODES:
        short, _, alias = name.partition(" (")
        items += (f'<div class="wm">{cell("CDEFGAB"[mode - 1], rows="none")}<b>{acc(short)}</b>'
                  f'<small>{acc(alias.rstrip(")"))}</small></div>')
    return f'<div class="whitemodes">{items}</div>'


def sec_modes():
    return f"""
  <h2>Modes</h2>
  <p class="lead">Play only white keys, from any key up to the same key an octave higher, and you get a mode:</p>
  {white_key_modes()}
  <p class="lead">Below, all seven start on C (bold degrees differ from major); in other keys the fingering shifts with the black keys.</p>
  <div class="mgrp">{mode_rows(MODES)}</div>
"""


def sec_jazz():
    return f"""
  <h2>Melodic minor and jazz scales</h2>
  <p class="lead">Melodic minor's modes are the main jazz scales over dominant and half-diminished chords; Phrygian dominant is from harmonic minor.</p>
  <div class="mgrp">{mode_rows(JAZZ_SCALES)}</div>
"""


def sec_more_scales():
    rows = []
    for i, (name, notes, formula, st, sound) in enumerate(MORE_SCALES):
        rows.append(
            f'<div class="xrow{" alt" if i % 2 else ""}">'
            f'<div class="mname"><b>{acc(name)}</b><span class="formula">{formula_html(formula)}</span></div>'
            + cells(notes.split(), rows="none")
            + f'<div class="msound"><span class="steps">{acc(st)}</span> · {acc(sound)}</div></div>'
        )
    return f"""
  <h2>Pentatonic, blues and symmetric scales</h2>
  <p class="lead">No standard fingering for these: keep the thumbs on white keys and pass them under right after a black key. W = whole step, H = half step, W+H = three half steps.</p>
  <div class="mgrp">{"".join(rows)}</div>
"""


def sec_arpeggios():
    def arp_rows(data):
        out = []
        for i, (key, other, notes, rh, lh) in enumerate(data):
            small = f"= {other}" if other else ""
            out.append(f'<div class="arow{" alt" if i % 2 else ""}">' + key_label(key, small)
                       + cells(notes.split(), fing(rh), fing(lh)) + "</div>")
        return "".join(out)

    inversions = "".join(
        '<div class="card">'
        f'<div class="card-t"><b>{t}</b></div>'
        + cells(n.split(), fing(r), fing(l))
        + "</div>"
        for t, n, r, l in ARP_INV
    )
    tables = {"major": ARP_MAJOR, "minor": ARP_MINOR}
    examples = ""
    for key, quality in ARP_EXAMPLES:
        _, _, notes, rh, lh = next(row for row in tables[quality] if row[0] == key)
        ns = notes.split()
        r2, l2 = two_octaves(fing(rh), "RH"), two_octaves(fing(lh), "LH")
        examples += (
            '<div class="ex">'
            f'<div class="ex-t"><b>{acc(key)} {quality}, two octaves</b></div>'
            + cells(ns + ns[1:], r2, l2)
            + f'<div class="ex-c"><i class="rh">RH</i> {repeat_text(r2, "RH")} · '
            f'<i class="lh">LH</i> {repeat_text(l2, "LH")}</div></div>'
        )
    return f"""
  <h2>Arpeggios</h2>
  <p class="lead">Root position, one octave. For more octaves the fingers repeat in groups of three, as written out below; only the first finger is special, and 5 is only for the very top (RH) or bottom (LH). F<span class="acc">♯</span> major and E<span class="acc">♭</span> minor are all black keys, so the thumb has to take one.</p>
  <div class="two8">{examples}</div>
  <div class="arps">
    <div><h3>Major</h3>{arp_rows(ARP_MAJOR)}</div>
    <div><h3>Minor</h3>{arp_rows(ARP_MINOR)}</div>
    <div class="arp-side">
      <h3>Inversions</h3>
      <p class="foot">C major shown; the same fingers work for F and G major and A, D and E minor.</p>
      {inversions}
      <p class="foot"><b>Left hand, 3 or 4?</b> The chord's 3rd takes 3 only when it's a major 3rd on a black key ({lh_three_keys()} major). Everywhere else it takes 4: a minor 3rd is narrow enough for 5 and 4, and on white keys 4 keeps the hand in its normal shape. Going up past the octave, that finger crosses over the thumb, and 3 makes the wider reach to a black key easier.</p>
      <p class="foot">Arpeggio fingerings follow Robert Kelley's standard arpeggio chart.</p>
    </div>
  </div>
"""


def sec_block_chords():
    cards_html = ""
    for group, cards in CHORD_CARDS:
        inner = ""
        for title, hint, notes, rh, lh in cards:
            inner += (
                '<div class="card">'
                f'<div class="card-t"><b>{acc(title)}</b><span>{acc(hint)}</span></div>'
                + cells(notes.split(), fing(rh), fing(lh))
                + "</div>"
            )
        cards_html += f'<div class="cgroup"><h3>{acc(group)}</h3><div class="cards">{inner}</div></div>'
    return f"""
  <h2>Block chords</h2>
  <div class="notes2 tight">
    <div><ul>
      <li>Right thumb on the bottom note, left thumb on the top note.</li>
      <li>Notes a step apart get neighbouring fingers.</li>
    </ul></div>
    <div><ul>
      <li>For the middle note, use 3. Switch to 2 when the wide gap (a 4th) is on the little-finger side.</li>
      <li>The shape decides the fingers, not the key. These work for major, minor, diminished and augmented chords alike.</li>
    </ul></div>
  </div>
  {cards_html}
"""


def sec_chord_types():
    def table(rows):
        body = "".join(
            f"<tr><th>{acc(n)}</th><td class='sym'>{acc(s)}</td><td>{acc(f)}</td><td>{acc(no)}</td></tr>"
            for n, s, f, no, _ in rows
        )
        return ('<div class="tscroll"><table class="tt ct2"><thead><tr><th>Chord</th><th>Symbol</th>'
                f"<th>Formula</th><th>In C</th></tr></thead><tbody>{body}</tbody></table></div>")

    half = (len(CHORD_TYPES) + 1) // 2
    return f"""
  <h2>Chord types</h2>
  <p class="lead">Three-note chords (major, minor, diminished, augmented, sus) use the triad and sus shapes in Block chords; four-note chords use the four-note, 6th and add9 shapes; chords with five notes or more are split between the hands, as in 9th, 11th and 13th chords.</p>
  <div class="tt2">{table(CHORD_TYPES[:half])}{table(CHORD_TYPES[half:])}</div>
"""


def sec_extended():
    rows = ""
    for sym, ln, lf, rn, rf, note in EXTENDED:
        rows += (
            '<div class="erow">'
            + key_label(sym, note)
            + '<div class="ehand"><span class="lab lh">LH</span>'
            + cells(ln.split(), l=fing(lf), rows="lh")
            + '</div><div class="ehand"><span class="lab rh">RH</span>'
            + cells(rn.split(), r=fing(rf), rows="rh")
            + "</div></div>"
        )
    return f"""
  <h2>9th, 11th and 13th chords</h2>
  <p class="lead">Too wide for one hand: the left hand plays the root plus the 5th or 7th, the right hand plays the notes on top.</p>
  <div class="ext">{rows}</div>
"""


def sec_sources():
    return """
  <p class="foot">Scale and chord fingerings are the common teaching standard; arpeggios follow Robert Kelley's standard chart; the faster chromatic fingering is from Chuan C. Chang's Fundamentals of Piano Practice. Other good fingerings exist, and hand size matters.</p>
"""


# (running-head section name, sections on that page). One entry per printed A4 page, in order.
# On the web every section that starts with an <h2> becomes its own expandable block.
PAGES = [
    ("Major scales", [sec_header, sec_major]),
    ("Minor scales", [sec_minor]),
    ("Melodic minor · Chromatic · More scales", [sec_melodic, sec_chromatic, sec_more_scales]),
    ("Modes · Jazz scales", [sec_modes, sec_jazz]),
    ("Arpeggios", [sec_arpeggios]),
    ("Chords", [sec_block_chords, sec_chord_types, sec_extended, sec_sources]),
]

# One-line hints shown next to each section's title on the web, where sections start closed.
SECTION_HINTS = {
    "sec_major": "all 12 keys",
    "sec_minor": "natural and harmonic, all 12 keys",
    "sec_melodic": "the two keys that need other fingers",
    "sec_chromatic": "standard, and a faster 1-2-3-4 fingering",
    "sec_block_chords": "triads, 7th chords, sus, add9",
    "sec_arpeggios": "all 24 keys, two-octave examples, inversions",
    "sec_modes": "all seven, with fingering",
    "sec_jazz": "melodic minor modes, Phrygian dominant",
    "sec_more_scales": "pentatonic, blues, whole-tone, diminished",
    "sec_chord_types": "22 chords with formulas",
    "sec_extended": "split between the hands",
}
