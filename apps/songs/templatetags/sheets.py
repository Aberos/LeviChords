"""Template filters for chord sheets."""

from django import template

from apps.songs.chords import SheetBlock, SheetLine, group_blocks

register = template.Library()


@register.filter
def blocks(lines: list[SheetLine]) -> list[SheetBlock]:
    """Group the sheet lines into blocks separated by blank lines."""
    return group_blocks(lines)
