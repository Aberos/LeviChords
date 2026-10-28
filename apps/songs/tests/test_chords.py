"""Tests for chord detection and transposition."""

import pytest

from apps.songs.chords import (
    LineKind,
    SheetLine,
    classify_line,
    clean_text,
    group_blocks,
    is_chord,
    normalize_semitones,
    parse_sheet,
    transpose_chord,
    transpose_key,
    transpose_line,
)


@pytest.mark.parametrize(
    "token",
    [
        "G",
        "Am7",
        "F#m7(b5)",
        "C/E",
        "Bb7M",
        "D4(9)",
        "Esus4",
        "A/C#",
        "C7/9",
        "Dº",
        "Ebmaj7",
        "G#dim",
        "G7M",
        "Em7(9)",
        "A7/4",
        "(G",
        "Em)",
        "(D/F#)",
    ],
)
def test_recognizes_chords(token: str) -> None:
    """Common chord spellings are recognized."""
    assert is_chord(token)


@pytest.mark.parametrize(
    "token",
    ["Deus", "Amor", "Senhor", "ti", "Cristo", "E|---", "(Aleluia)", "("],
)
def test_rejects_words(token: str) -> None:
    """Lyric words are not mistaken for chords."""
    assert not is_chord(token)


@pytest.mark.parametrize(
    ("line", "kind"),
    [
        ("G       D/F#    Em", LineKind.CHORDS),
        ("[Intro] A  E  F#m  D  (2x)", LineKind.CHORDS),
        ("Grande é o Senhor", LineKind.LYRICS),
        ("Em ti confiarei", LineKind.LYRICS),
        ("( G  D  Em )", LineKind.CHORDS),
        ("(G  D  Em)", LineKind.CHORDS),
        ("Intro: G  D  Em  C", LineKind.CHORDS),
        ("G  /  D  /  Em", LineKind.CHORDS),
        ("Disse: Senhor", LineKind.LYRICS),
        ("(Aleluia)", LineKind.LYRICS),
        ("E|-----3-----2-----|", LineKind.TAB),
        ("B|-10---10-13-------13---| ", LineKind.TAB),
        ("E|", LineKind.LYRICS),
        ("[Refrão]", LineKind.SECTION),
        ("   ", LineKind.BLANK),
    ],
)
def test_classifies_lines(line: str, kind: LineKind) -> None:
    """Lines are classified by their content."""
    assert classify_line(line) is kind


@pytest.mark.parametrize(
    ("chord", "semitones", "flats", "expected"),
    [
        ("C", 2, None, "D"),
        ("Am7", 3, None, "Cm7"),
        ("D/F#", 2, None, "E/G#"),
        ("Bb", 2, None, "C"),
        ("Bb", 1, None, "B"),
        ("A", 1, True, "Bb"),
        ("F#m7(b5)", -1, None, "Fm7(b5)"),
        ("C", 12, None, "C"),
        ("[Intro]", 2, None, "[Intro]"),
        ("(D/F#)", 2, None, "(E/G#)"),
        ("(G", 2, None, "(A"),
        ("Em)", 2, None, "F#m)"),
    ],
)
def test_transposes_chords(
    chord: str, semitones: int, flats: bool | None, expected: str
) -> None:
    """Chords keep their suffix and bass when transposed."""
    assert transpose_chord(chord, semitones, flats) == expected


@pytest.mark.parametrize(
    ("key", "semitones", "expected"),
    [
        ("G", -2, "F"),
        ("C", 3, "Eb"),
        ("E", 2, "F#"),
        ("Am", 2, "Bm"),
        ("A", 1, "Bb"),
        ("F", 1, "F#"),
    ],
)
def test_transposes_keys(key: str, semitones: int, expected: str) -> None:
    """Keys use their most common spelling."""
    assert transpose_key(key, semitones) == expected


@pytest.mark.parametrize(
    ("semitones", "expected"), [(0, 0), (6, 6), (7, -5), (-6, 6), (13, 1)]
)
def test_normalizes_semitones(semitones: int, expected: int) -> None:
    """Shifts are kept between -5 and +6."""
    assert normalize_semitones(semitones) == expected


def test_transpose_line_keeps_columns() -> None:
    """Chords stay above the same syllables when there is room."""
    assert transpose_line("C       G", 1) == "C#      G#"


def test_transpose_line_keeps_a_space_between_chords() -> None:
    """Longer chords push the next one while keeping a separator."""
    assert transpose_line("C G", 1) == "C# G#"


def test_parse_sheet_uses_flats_for_flat_keys() -> None:
    """The transposed key decides the accidental of every chord."""
    lines = parse_sheet("C  G\nLetra", 3, "C")
    assert [line.text for line in lines] == ["Eb Bb", "Letra"]
    assert [line.kind for line in lines] == [
        LineKind.CHORDS,
        LineKind.LYRICS,
    ]


def test_parse_sheet_reads_a_cifra_club_sheet() -> None:
    """A sheet pasted from Cifra Club keeps its layout and is transposed."""
    pasted = (
        "[Intro] G7M  D/F#  Em7  C9  (2x)\n"
        "\n"
        "[Tab - Intro]\n"
        "E|-----3-----2-----|\n"
        "\n"
        "[Primeira Parte]\n"
        "\u00a0 \u00a0 G7M\u00a0 \u00a0 \u00a0 D/F#\n"
        "Grande é o Senhor\n"
        "( Em  C )\n"
    )
    lines = parse_sheet(pasted, 2, "G")
    assert [line.kind for line in lines] == [
        LineKind.CHORDS,
        LineKind.BLANK,
        LineKind.SECTION,
        LineKind.TAB,
        LineKind.BLANK,
        LineKind.SECTION,
        LineKind.CHORDS,
        LineKind.LYRICS,
        LineKind.CHORDS,
    ]
    assert lines[0].text == "[Intro] A7M  E/G#  F#m7 D9  (2x)"
    assert lines[3].text == "E|-----3-----2-----|"
    assert lines[6].text == "    A7M      E/G#"
    assert lines[8].text == "( F#m D )"


def test_clean_text_removes_invisible_characters() -> None:
    """Zero width spaces and special spaces copied from sites go away."""
    assert clean_text("\u200bG\u00a0 D\ufeff") == "G  D"


def test_parse_sheet_ignores_zero_width_spaces() -> None:
    """Chord lines starting with a zero width space are still chords."""
    lines = parse_sheet("\u200b[Intro] Am  Dm\n\u200bG      E7", 2)
    assert [line.kind for line in lines] == [
        LineKind.CHORDS,
        LineKind.CHORDS,
    ]
    assert lines[1].text == "A      F#7"


def test_group_blocks_splits_on_blank_lines() -> None:
    """Blank lines separate the blocks and are not kept."""
    lines = parse_sheet("\n[Intro] G\n\n\nG\nLetra\n\n")
    blocks = group_blocks(lines)
    assert [[line.text for line in block.lines] for block in blocks] == [
        ["[Intro] G"],
        ["G", "Letra"],
    ]


def test_group_blocks_of_an_empty_sheet() -> None:
    """An empty sheet has no blocks."""
    assert group_blocks([SheetLine(kind=LineKind.BLANK, text="")]) == []


@pytest.mark.parametrize(
    ("text", "is_tab"),
    [
        ("Parte 1 de 2\n   Am    Dm\nE|---7-8---|\nB|-10------|", True),
        ("[Tab - Intro - 2x]", True),
        ("[Refrão]\nG    D\nGrande é o Senhor", False),
    ],
)
def test_blocks_know_when_they_are_tablature(text: str, is_tab: bool) -> None:
    """Blocks with tablature lines or a tab label can be hidden."""
    (block,) = group_blocks(parse_sheet(text))
    assert block.is_tab is is_tab
