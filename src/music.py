"""Pitch helpers shared by every sheet.

Notes are strings such as "C", "F♯", "B♭" or "F𝄪". Pitch classes are 0–11 with C = 0.
"""

LET = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ACC = {"♯": 1, "♭": -1, "𝄪": 2, "𝄫": -2}
BLACK = {1, 3, 6, 8, 10}


def pc(n):
    return (LET[n[0]] + sum(ACC[c] for c in n[1:])) % 12


def is_black(n):
    return pc(n) in BLACK


def black_pc(p):
    return p % 12 in BLACK


def steps(ns):
    """Half steps between neighbouring notes."""
    return [(pc(b) - pc(a)) % 12 for a, b in zip(ns, ns[1:])]
