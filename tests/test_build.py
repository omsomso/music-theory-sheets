"""The sheets' checks must pass on the real data and catch the kinds of mistakes they exist for."""
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import build  # noqa: E402
import fingering  # noqa: E402

TABLES = ("MAJOR", "MINOR", "MELODIC", "ARP_MAJOR", "ARP_MINOR", "CHORD_CARDS", "CHORD_TYPES", "EXTENDED",
          "MODES", "JAZZ_SCALES", "MORE_SCALES", "CHROMATIC_FAST")


def replace_row(rows, key, index, value):
    """Return rows with field `index` of the row whose first field is `key` set to `value`."""
    out = []
    for row in rows:
        if row[0] == key:
            row = row[:index] + (value,) + row[index + 1:]
        out.append(row)
    return out


class FingeringChecks(unittest.TestCase):
    def setUp(self):
        self.saved = {name: copy.deepcopy(getattr(fingering, name)) for name in TABLES}

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(fingering, name, value)

    def assertProblem(self, text):
        problems = build.validate()
        self.assertTrue(any(text in p for p in problems), f"expected {text!r} in {problems}")

    def test_sheet_data_passes(self):
        self.assertEqual(build.validate(), [])

    def test_thumb_on_black_key_is_rejected(self):
        # The left hand from the original PDF's C# minor row: thumb lands on F#.
        fingering.MINOR = replace_row(fingering.MINOR, "C♯", 6, "43213214")
        self.assertProblem("C♯ minor LH: thumb on black key F♯")

    def test_impossible_finger_order_is_rejected(self):
        fingering.MAJOR = replace_row(fingering.MAJOR, "G", 4, "12312354")
        self.assertProblem("G major RH: awkward move")

    def test_wrong_scale_notes_are_rejected(self):
        fingering.MAJOR = replace_row(fingering.MAJOR, "D", 3, "D E F G A B C♯ D")
        self.assertProblem("D major: wrong notes")

    def test_melodic_exceptions_must_match_the_fingerings(self):
        fingering.MELODIC = fingering.MELODIC[:1]  # drop C#, which really needs its own fingering
        self.assertProblem("melodic exceptions mismatch")

    def test_chord_formula_must_match_its_notes(self):
        fingering.CHORD_TYPES = replace_row(fingering.CHORD_TYPES, "Dominant seventh", 3, "C E G B")
        self.assertProblem("C7: formula")

    def test_step_apart_notes_need_neighbouring_fingers(self):
        cards = copy.deepcopy(fingering.CHORD_CARDS)
        group, rows = cards[2]
        rows[0] = ("sus2", "Csus2", "C D G", "135", "541")  # C and D a step apart on fingers 1 and 3
        cards[2] = (group, rows)
        fingering.CHORD_CARDS = cards
        self.assertProblem("notes a step apart need neighbouring fingers")

    def test_extended_voicing_label_must_be_true(self):
        fingering.EXTENDED = replace_row(fingering.EXTENDED, "C9", 1, "C")  # drops the B-flat
        fingering.EXTENDED = replace_row(fingering.EXTENDED, "C9", 2, "5")
        self.assertProblem("C9: voicing leaves out")

    def test_arpeggio_thumb_on_black_key_is_rejected(self):
        fingering.ARP_MINOR = replace_row(fingering.ARP_MINOR, "C♯", 3, "1235")
        self.assertProblem("C♯ minor arpeggio RH: thumb on black key")

    def test_two_octave_extension_follows_the_references(self):
        # Kelley: the pattern repeats every three notes; 5 only at a start, stop or turn.
        self.assertEqual(fingering.two_octaves([1, 2, 3, 5], "RH"), [1, 2, 3, 1, 2, 3, 5])
        self.assertEqual(fingering.two_octaves([5, 4, 2, 1], "LH"), [5, 4, 2, 1, 4, 2, 1])
        self.assertEqual(fingering.two_octaves([2, 1, 2, 4], "RH"), [2, 1, 2, 4, 1, 2, 4])
        self.assertEqual(fingering.two_octaves([2, 1, 4, 2], "LH"), [2, 1, 4, 2, 1, 4, 2])

    def test_left_hand_third_rule_is_enforced(self):
        # D major's 3rd (F#) is a major 3rd on a black key, so the left hand must use 3 there.
        fingering.ARP_MAJOR = replace_row(fingering.ARP_MAJOR, "D", 4, "5421")
        self.assertProblem("D major arpeggio LH: 3rd (F♯) should take 3")

    def test_fingering_rules_must_reproduce_the_hand_written_scales(self):
        # 2 3 1 2 3 4 1 2 is playable in E-flat (thumbs on G and D) but isn't the standard
        # 3 1 2 3 4 1 2 3; the rules behind the generated mode fingerings must catch that.
        fingering.MAJOR = replace_row(fingering.MAJOR, "E♭", 4, "23123412")
        self.assertProblem("fingering rules don't reproduce E♭ major")

    def test_generated_fingerings_for_modes(self):
        lydian = fingering.auto_fingering("C D E F♯ G A B C".split())
        locrian = fingering.auto_fingering("C D♭ E♭ F G♭ A♭ B♭ C".split())
        self.assertEqual(lydian, ([1, 2, 3, 4, 1, 2, 3, 4], [5, 4, 3, 2, 1, 3, 2, 1]))
        self.assertEqual(locrian, ([1, 2, 3, 1, 2, 3, 4, 5], [4, 3, 2, 1, 4, 3, 2, 1]))

    def test_mode_formula_and_parent_are_checked(self):
        fingering.MODES = replace_row(fingering.MODES, "Dorian", 3, "1 2 ♭3 4 5 ♭6 ♭7")
        fingering.JAZZ_SCALES = replace_row(fingering.JAZZ_SCALES, "Lydian dominant", 2, "C D E F♯ G A B C")
        self.assertProblem("Dorian: formula")
        self.assertProblem("Lydian dominant: notes are not mode 4 of melodic minor")

    def test_fast_chromatic_keeps_thumbs_on_white_keys(self):
        # Shifting the groups by one note puts the thumb on F#.
        fingering.CHROMATIC_FAST = ("E F F♯ G G♯ A A♯ B C C♯ D D♯ E", "2312341231212")
        self.assertProblem("fast chromatic RH: thumb on black key F♯")

    def test_chord_type_shape_must_fit_its_size(self):
        fingering.CHORD_TYPES = replace_row(fingering.CHORD_TYPES, "Ninth", 4, "Triad")
        self.assertProblem("C9: piano shape 'Triad' doesn't fit a 5-note chord")

    def test_modes_must_be_in_mode_order(self):
        fingering.MODES = list(reversed(fingering.MODES))
        self.assertProblem("modes must be listed in mode order")

    def test_more_scales_steps_are_checked(self):
        fingering.MORE_SCALES = replace_row(fingering.MORE_SCALES, "Blues", 3, "W+H W H H W W+H")
        self.assertProblem("Blues: steps")

    def test_left_hand_note_names_the_right_keys(self):
        plain = re.sub(r"<[^>]+>", "", fingering.lh_three_keys())
        self.assertEqual(plain, "D, A, E, B, F♯")

    def test_arpeggio_that_breaks_over_two_octaves_is_rejected(self):
        # 1 2 3 4 is fine for one octave of C but can't continue: 4 would have to jump back to 2.
        fingering.ARP_MAJOR = replace_row(fingering.ARP_MAJOR, "C", 3, "1234")
        self.assertProblem("C major arpeggio (two octaves) RH: awkward move")


class Outputs(unittest.TestCase):
    def test_every_sheet_writes_its_three_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(build.main(["build.py", tmp]), 0)
            for sheet in build.SHEETS:
                screen = (Path(tmp) / f"{sheet.SLUG}.html").read_text(encoding="utf-8")
                printed = (Path(tmp) / f"{sheet.SLUG}-print.html").read_text(encoding="utf-8")
                preview = (Path(tmp) / f"{sheet.SLUG}-preview.html").read_text(encoding="utf-8")
                self.assertTrue(screen.startswith(f"<title>{sheet.TITLE}</title>"))
                self.assertNotIn("<body", screen)  # the artifact host adds its own document skeleton
                self.assertIn('class="sheet print"', printed)
                self.assertEqual(printed.count('<section class="page'), len(sheet.PAGES))
                self.assertIn("<body>", preview)
                self.assertIn('content="noindex, nofollow"', preview)  # the site is unlisted
                # The site page links back to the index and to its PDF; the claude.ai page and
                # the print version have no site navigation.
                self.assertIn('class="sitenav"', preview)
                self.assertIn('href="index.html"', preview)
                self.assertIn(f'href="{sheet.SLUG}.pdf"', preview)
                self.assertNotIn('class="sitenav"', screen)
                self.assertNotIn('class="sitenav"', printed)
                # Web versions: every titled section is a closed, expandable block with a unique
                # id; the print version keeps plain pages.
                titled = sum(1 for _, secs in sheet.PAGES for s in secs if build.H2.match(s()))
                for web in (screen, preview):
                    self.assertEqual(web.count('<details class="sec"'), titled)
                    self.assertNotIn("<details class=\"sec\" open", web)
                    ids = re.findall(r'<details class="sec" id="([^"]+)"', web)
                    self.assertEqual(len(ids), len(set(ids)))
                    self.assertIn('id="open-all"', web)
                self.assertNotIn("<details", printed)
            index = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            self.assertIn('content="noindex, nofollow"', index)
            for sheet in build.SHEETS:
                self.assertIn(f'href="{sheet.SLUG}.html"', index)
                self.assertIn(f'href="{sheet.SLUG}.pdf"', index)

    def test_sheet_modules_provide_what_build_needs(self):
        slugs = [s.SLUG for s in build.SHEETS]
        self.assertEqual(len(slugs), len(set(slugs)))
        for sheet in build.SHEETS:
            for attr in ("SLUG", "TITLE", "NAME", "DESCRIPTION", "PAGES", "validate", "summary"):
                self.assertTrue(hasattr(sheet, attr), f"{sheet.__name__} lacks {attr}")


if __name__ == "__main__":
    unittest.main()
