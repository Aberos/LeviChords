"""Chord detection and transposition for plain text chord sheets."""

import re
from dataclasses import dataclass
from enum import StrEnum

SHARP_NOTES: tuple[str, ...] = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)
FLAT_NOTES: tuple[str, ...] = (
    "C",
    "Db",
    "D",
    "Eb",
    "E",
    "F",
    "Gb",
    "G",
    "Ab",
    "A",
    "Bb",
    "B",
)
FLAT_KEYS: frozenset[str] = frozenset(
    {"F", "Bb", "Eb", "Ab", "Db", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm"}
)
MIN_SEMITONES = -5
MAX_SEMITONES = 6

_LETTER_SEMITONES: dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}
_ACCIDENTAL_OFFSET: dict[str, int] = {"": 0, "#": 1, "b": -1}

_NOTE = r"[A-G][#b]?"
_SUFFIX = r"(?:maj|min|dim|aug|sus|add|/[0-9]+|[mM0-9º°+#b(),-])*"

CHORD_PATTERN = re.compile(
    rf"^(?P<open>\(?)(?P<root>{_NOTE})(?P<suffix>{_SUFFIX})"
    rf"(?:/(?P<bass>{_NOTE}))?(?P<close>\)?)$"
)
KEY_PATTERN = re.compile(r"^(?P<root>[A-G][#b]?)(?P<minor>m?)$")
SECTION_PATTERN = re.compile(r"^\s*\[[^\]]+\]\s*$")
TAB_PATTERN = re.compile(r"^\s*[A-Ga-g][#b]?\|.*-{3,}")
TAB_SECTION_PATTERN = re.compile(r"^\s*\[\s*tab\b", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"\[[^\]]*\]|\S+")
INVISIBLE_CHARACTERS = "\u200b\u200c\u200d\u2060\ufeff"
SPECIAL_SPACES = "\xa0\u2002\u2003\u2007\u2009\u202f"
TEXT_CLEANUP = str.maketrans(
    dict.fromkeys(INVISIBLE_CHARACTERS, "")
    | dict.fromkeys(SPECIAL_SPACES, " ")
)
AUXILIARY_PATTERN = re.compile(
    r"^(?:\[[^\]]*\]|\|+|\(?(?:\d+x|x\d+)\)?|-+|\.+|%|[()/]|[^\W\d_]+:)$",
    re.IGNORECASE,
)


class LineKind(StrEnum):
    """Kind of a chord sheet line."""

    CHORDS = "chords"
    LYRICS = "lyrics"
    SECTION = "section"
    TAB = "tab"
    BLANK = "blank"


@dataclass(frozen=True)
class SheetLine:
    """Chord sheet line ready to be displayed."""

    kind: LineKind
    text: str


@dataclass(frozen=True)
class SheetBlock:
    """Group of lines between blank lines, such as a verse or a riff."""

    lines: list[SheetLine]

    @property
    def is_tab(self) -> bool:
        """Return whether the block is a tablature, so it can be hidden."""
        return any(
            line.kind is LineKind.TAB
            or (
                line.kind is LineKind.SECTION
                and TAB_SECTION_PATTERN.match(line.text) is not None
            )
            for line in self.lines
        )


def note_index(note: str) -> int:
    """Return the chromatic position of a note, from 0 to 11."""
    return (_LETTER_SEMITONES[note[0]] + _ACCIDENTAL_OFFSET[note[1:]]) % 12


def transpose_note(note: str, semitones: int, flats: bool) -> str:
    """Move a note by the given semitones using sharps or flats."""
    scale = FLAT_NOTES if flats else SHARP_NOTES
    return scale[(note_index(note) + semitones) % 12]


def is_chord(token: str) -> bool:
    """Return whether the token is a chord such as ``F#m7(b5)/E``."""
    return CHORD_PATTERN.match(token) is not None


def is_valid_key(key: str) -> bool:
    """Return whether the text is a key such as ``G``, ``Bb`` or ``F#m``."""
    return KEY_PATTERN.match(key) is not None


def normalize_semitones(semitones: int) -> int:
    """Bring any shift into the range from -5 to +6 semitones."""
    return (semitones - MIN_SEMITONES) % 12 + MIN_SEMITONES


def transpose_chord(
    chord: str, semitones: int, flats: bool | None = None
) -> str:
    """Transpose a chord, keeping its suffix, bass note and parentheses.

    When ``flats`` is ``None`` the accidental of the original root is kept.
    Tokens that are not chords are returned unchanged.
    """
    match = CHORD_PATTERN.match(chord)
    if match is None or semitones % 12 == 0:
        return chord
    root = match["root"]
    use_flats = root.endswith("b") if flats is None else flats
    result = (
        match["open"]
        + transpose_note(root, semitones, use_flats)
        + match["suffix"]
    )
    if match["bass"]:
        result += "/" + transpose_note(match["bass"], semitones, use_flats)
    return result + match["close"]


def transpose_key(key: str, semitones: int) -> str:
    """Return the resulting key using its most common spelling."""
    match = KEY_PATTERN.match(key)
    if match is None or semitones % 12 == 0:
        return key
    minor = match["minor"]
    with_flats = transpose_note(match["root"], semitones, True) + minor
    if with_flats in FLAT_KEYS:
        return with_flats
    return transpose_note(match["root"], semitones, False) + minor


def _is_auxiliary(token: str) -> bool:
    """Return whether the token may appear among chords, like ``(2x)``."""
    return AUXILIARY_PATTERN.match(token) is not None


def clean_text(text: str) -> str:
    """Remove invisible characters and turn special spaces into spaces.

    Sites like Cifra Club add zero width spaces at the start of lines,
    which would hide the chords from the line classification.
    """
    return text.translate(TEXT_CLEANUP)


def classify_line(line: str) -> LineKind:
    """Classify a line as chords, lyrics, section, tablature or blank."""
    if not line.strip():
        return LineKind.BLANK
    if SECTION_PATTERN.match(line):
        return LineKind.SECTION
    if TAB_PATTERN.match(line):
        return LineKind.TAB
    tokens = TOKEN_PATTERN.findall(line)
    has_chord = any(is_chord(token) for token in tokens)
    only_chords = all(is_chord(t) or _is_auxiliary(t) for t in tokens)
    if has_chord and only_chords:
        return LineKind.CHORDS
    return LineKind.LYRICS


def transpose_line(
    line: str, semitones: int, flats: bool | None = None
) -> str:
    """Transpose every chord of a line, keeping columns when possible."""
    result = ""
    for match in TOKEN_PATTERN.finditer(line):
        start = match.start()
        if len(result) < start:
            result += " " * (start - len(result))
        elif result:
            result += " "
        result += transpose_chord(match.group(), semitones, flats)
    return result


def parse_sheet(
    text: str, semitones: int = 0, key: str = ""
) -> list[SheetLine]:
    """Split a chord sheet into classified lines, transposing the chords.

    When the original key is known, the transposed key decides between
    sharps and flats.
    """
    flats = (
        transpose_key(key, semitones) in FLAT_KEYS
        if is_valid_key(key)
        else None
    )
    lines: list[SheetLine] = []
    for raw in clean_text(text).splitlines():
        content = raw.expandtabs(4).rstrip()
        kind = classify_line(content)
        if kind is LineKind.CHORDS:
            content = transpose_line(content, semitones, flats)
        lines.append(SheetLine(kind=kind, text=content))
    return lines


def group_blocks(lines: list[SheetLine]) -> list[SheetBlock]:
    """Split the lines into blocks separated by blank lines.

    Each block keeps the chords together with their lyrics, so the reading
    mode can lay the blocks out in columns without breaking them.
    """
    blocks: list[SheetBlock] = []
    current: list[SheetLine] = []
    for line in lines:
        if line.kind is LineKind.BLANK:
            if current:
                blocks.append(SheetBlock(lines=current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(SheetBlock(lines=current))
    return blocks
