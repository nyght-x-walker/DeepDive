"""Deterministic data model and reusable visual components for the
Phase 1 boundary animation.

Two layers, clearly separated in this file:

- Data layer (pure Python, no Manim): mirrors the algorithm of
  ``src/phase1_boundary_model.cpp`` exactly.
- Visual layer (Manim): scalable mobjects that render the data layer.
  The data layer remains usable without Manim; importing this module
  does import Manim because both layers share this file.

Data-layer algorithm, as in the C++ program:

1. One contiguous, zero-initialized array of TOTAL_MEMORY_SIZE bytes.
2. Three logical regions written into it (buffer, criticalFlag, buffer2).
3. A copy of the input capped at the array size via
   ``min(len(input), TOTAL_MEMORY_SIZE)``.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Line,
    Rectangle,
    Square,
    Text,
    Triangle,
    VGroup,
)

from . import config


# ---------------------------------------------------------------------------
# Region and cell representation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MemoryRegion:
    """A named logical slice of the contiguous memory model."""

    name: str
    offset: int
    size: int
    color: str

    @property
    def end(self) -> int:
        """Exclusive end offset of this region."""
        return self.offset + self.size


@dataclass(frozen=True)
class ByteCell:
    """One byte of the memory model: position, value, owning region."""

    offset: int
    value: int
    region: str


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_regions(regions: List[MemoryRegion]) -> List[MemoryRegion]:
    """Check that regions are non-negative, fit in the total array,
    and do not overlap. Raises ValueError otherwise."""
    if not regions:
        raise ValueError("at least one region is required")
    for region in regions:
        if region.offset < 0 or region.size < 0:
            raise ValueError(
                f"region '{region.name}' has a negative offset or size"
            )
        if region.end > config.TOTAL_MEMORY_SIZE:
            raise ValueError(
                f"region '{region.name}' (offset {region.offset}, "
                f"size {region.size}) exceeds TOTAL_MEMORY_SIZE="
                f"{config.TOTAL_MEMORY_SIZE}"
            )
    for i, left in enumerate(regions):
        for right in regions[i + 1:]:
            if left.offset < right.end and right.offset < left.end:
                raise ValueError(
                    f"regions '{left.name}' and '{right.name}' overlap"
                )
    return regions


def validate_input_lengths(
    expected: Dict[str, int] = None,
) -> Dict[str, int]:
    """Check that each input's actual length matches its expected
    length. Raises ValueError otherwise."""
    expected = expected if expected is not None else config.EXPECTED_INPUT_LENGTHS
    for text, length in expected.items():
        if len(text) != length:
            raise ValueError(
                f"input {text!r} has length {len(text)}, expected {length}"
            )
    return expected


# ---------------------------------------------------------------------------
# Region construction and boundary queries
# ---------------------------------------------------------------------------


def build_regions() -> List[MemoryRegion]:
    """The three logical regions, in physical order."""
    return validate_regions(
        [
            MemoryRegion(
                name="buffer",
                offset=config.BUFFER_OFFSET,
                size=config.BUFFER_SIZE,
                color=config.COLOR_BUFFER,
            ),
            MemoryRegion(
                name="criticalFlag",
                offset=config.FLAG_OFFSET,
                size=config.FLAG_SIZE,
                color=config.COLOR_FLAG,
            ),
            MemoryRegion(
                name="buffer2",
                offset=config.SECOND_BUFFER_OFFSET,
                size=config.SECOND_BUFFER_SIZE,
                color=config.COLOR_SECOND_BUFFER,
            ),
        ]
    )


REGIONS: List[MemoryRegion] = build_regions()


def region_bounds(region: MemoryRegion) -> Tuple[int, int]:
    """Inclusive start and exclusive end offsets of a region."""
    return (region.offset, region.end)


def region_for_offset(offset: int) -> str:
    """Name of the region containing ``offset``; raises ValueError
    if the offset lies outside every region."""
    for region in REGIONS:
        if region.offset <= offset < region.end:
            return region.name
    raise ValueError(
        f"offset {offset} is not inside any region "
        f"(total memory size {config.TOTAL_MEMORY_SIZE})"
    )


# ---------------------------------------------------------------------------
# Byte conversion and formatting
# ---------------------------------------------------------------------------


def char_to_byte(char: str) -> int:
    """Deterministic conversion of one ASCII character to its byte
    value (0-127; printable ASCII is the program's domain)."""
    if len(char) != 1:
        raise ValueError(f"expected a single character, got {char!r}")
    value = ord(char)
    if value < 0 or value > 255:
        raise ValueError(f"character {char!r} is not a byte value")
    return value


def string_to_bytes(text: str) -> List[int]:
    """Convert a string to its list of byte values."""
    return [char_to_byte(char) for char in text]


def hex_byte(value: int) -> str:
    """Two-digit, zero-padded lowercase hexadecimal, matching the
    C++ program's ``printHexByte`` (``std::hex`` default casing)."""
    if not 0 <= value <= 255:
        raise ValueError(f"byte value out of range: {value}")
    return f"{value:02x}"


def ascii_char(value: int) -> str:
    """Printable ASCII character for a byte, or '.' for non-printable
    bytes, exactly like the C++ program's memory dump."""
    if not 0 <= value <= 255:
        raise ValueError(f"byte value out of range: {value}")
    return chr(value) if 32 <= value <= 126 else "."


# ---------------------------------------------------------------------------
# Memory model construction
# ---------------------------------------------------------------------------


def _write_at(memory: List[int], offset: int, capacity: int, data: List[int]) -> None:
    """Write at most ``capacity`` bytes of ``data`` at ``offset``,
    mirroring the C++ ``memcpy(..., std::min(size, capacity))``."""
    count = min(len(data), capacity)
    memory[offset:offset + count] = data[:count]


def build_memory(input_text: str) -> List[int]:
    """Return the exact TOTAL_MEMORY_SIZE-byte array the C++ program
    produces for ``input_text``: initialization of the three regions
    followed by the capped input copy."""
    if not isinstance(input_text, str):
        raise TypeError(f"input_text must be str, got {type(input_text).__name__}")

    memory = [0] * config.TOTAL_MEMORY_SIZE

    _write_at(
        memory,
        config.BUFFER_OFFSET,
        config.BUFFER_SIZE,
        string_to_bytes(config.INITIAL_BUFFER),
    )
    _write_at(
        memory,
        config.FLAG_OFFSET,
        config.FLAG_SIZE,
        list(config.INITIAL_FLAG_BYTES),
    )
    _write_at(
        memory,
        config.SECOND_BUFFER_OFFSET,
        config.SECOND_BUFFER_SIZE,
        string_to_bytes(config.INITIAL_SECOND_BUFFER),
    )

    copy_len = copy_length(input_text)
    _write_at(memory, 0, copy_len, string_to_bytes(input_text[:copy_len]))

    return memory


def build_memory_cells(input_text: str) -> List[ByteCell]:
    """Return one ByteCell per offset (00..TOTAL_MEMORY_SIZE-1)."""
    memory = build_memory(input_text)
    return [
        ByteCell(offset=i, value=memory[i], region=region_for_offset(i))
        for i in range(len(memory))
    ]


# ---------------------------------------------------------------------------
# Input helpers (quantities the animation must display)
# ---------------------------------------------------------------------------


def input_length(text: str) -> int:
    return len(text)


def input_fits(text: str) -> bool:
    """True when the input length does not exceed the logical buffer."""
    return len(text) <= config.BUFFER_SIZE


def excess_bytes(text: str) -> int:
    """Number of bytes beyond the logical buffer (0 when it fits)."""
    return max(0, len(text) - config.BUFFER_SIZE)


def copy_length(text: str) -> int:
    """Bytes actually copied into the model: capped at the array size."""
    return min(len(text), config.TOTAL_MEMORY_SIZE)


# ---------------------------------------------------------------------------
# Visual layer: reusable Manim components.
#
# All components are VGroups so scenes can position, scale, and animate
# them with standard Manim calls. Sizes derive from constructor
# parameters (no hardcoded positions); byte/hex/offset text always uses
# the monospaced font.
# ---------------------------------------------------------------------------


def _mono_text(text: str, font_size: float, color: str = config.COLOR_TEXT) -> Text:
    """Monospaced Text with the project's default font and color."""
    return Text(text, font=config.FONT_MONO, font_size=font_size, color=color)


def _char_font_for(side_length: float) -> int:
    """Font size that keeps a single character inside a cell."""
    return max(10, int(side_length * 36))


class MemoryByteCell(VGroup):
    """One byte cell: a square with an optional centered ASCII character
    and an optional offset label beneath it.

    The displayed character follows the program's dump rule
    (printable ASCII, otherwise '.'). Call ``set_value`` or ``clear``
    to update the content for animations.
    """

    def __init__(
        self,
        value: Optional[int] = None,
        offset: Optional[int] = None,
        side_length: float = 0.55,
        font_size: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.side_length = side_length
        self.offset = offset
        self.square = Square(
            side_length=side_length,
            fill_color=config.COLOR_CELL_FILL,
            fill_opacity=1.0,
            stroke_color=config.COLOR_CELL_STROKE,
            stroke_width=2,
        )
        self.add(self.square)

        self.char_text = _mono_text(
            " ", font_size=font_size or _char_font_for(side_length)
        )
        self.char_text.move_to(self.square.get_center())
        self.add(self.char_text)

        self.offset_text: Optional[Text] = None
        if offset is not None:
            self.offset_text = _mono_text(
                f"{offset:02d}", font_size=max(11, int(side_length * 26)),
                color=config.COLOR_OFFSET_LABEL,
            )
            self.offset_text.next_to(self.square, DOWN, buff=0.06)
            self.add(self.offset_text)

        if value is not None:
            self.set_value(value)

    def set_value(self, value: int) -> "MemoryByteCell":
        """Display the byte as its ASCII character (program dump rule)."""
        self.char_text.text = ascii_char(value)
        return self

    def clear(self) -> "MemoryByteCell":
        """Hide the character, leaving an empty cell."""
        self.char_text.text = " "
        return self


class ByteLabel(VGroup):
    """Character and hexadecimal representation of one byte, stacked.

    Monospaced throughout; used wherever a byte must be shown in both
    forms at once (e.g., a focused cell or a legend).
    """

    def __init__(self, value: int, font_size: int = 18) -> None:
        super().__init__()
        self.value = value
        self.hex_text = _mono_text(hex_byte(value), font_size=font_size)
        self.char_text = _mono_text(ascii_char(value), font_size=font_size)
        self.hex_text.move_to(ORIGIN)
        self.char_text.next_to(self.hex_text, DOWN, buff=0.08)
        self.add(self.hex_text, self.char_text)

    def set_value(self, value: int) -> "ByteLabel":
        """Update both representations to ``value``."""
        self.value = value
        self.hex_text.text = hex_byte(value)
        self.char_text.text = ascii_char(value)
        return self


class LabeledMemoryRegion(VGroup):
    """A colored region panel with a text title and a monospaced size
    tag above it.

    The title is scaled to fit the panel so long names (e.g.
    ``criticalFlag``) never overflow or clip.
    """

    def __init__(
        self,
        name: str,
        size: int,
        color: str,
        width: float = 4.0,
        height: float = 0.95,
        title_font_size: int = 26,
    ) -> None:
        super().__init__()
        self.name = name
        self.size = size
        self.panel = Rectangle(
            width=width,
            height=height,
            fill_color=color,
            fill_opacity=0.16,
            stroke_color=color,
            stroke_width=3,
        )
        self.title = Text(
            name, font=config.FONT_SANS, font_size=title_font_size, color=color
        )
        self.title.scale_to_fit_width(max(0.4, width - 0.5))
        self.title.next_to(self.panel, UP, buff=0.12)
        self.size_tag = _mono_text(
            f"{size} bytes",
            font_size=max(12, title_font_size - 8),
            color=config.COLOR_OFFSET_LABEL,
        )
        self.size_tag.next_to(self.title, UP, buff=0.04)
        self.add(self.panel, self.title, self.size_tag)


class MemoryLayout(VGroup):
    """The complete 20-byte memory model: region panels, byte cells,
    offset labels, and region titles.

    Cells are addressable by offset (``cell(offset)``) and panels by
    region name (``panel(name)``) so scenes can animate individual
    bytes. Layout geometry is relative; scenes only position the whole
    group.
    """

    def __init__(
        self,
        regions: List[MemoryRegion] = None,
        cell_side: float = 0.55,
        cell_gap: float = 0.08,
        panel_padding: float = 0.25,
        show_offsets: bool = True,
        title_font_size: int = 26,
    ) -> None:
        super().__init__()
        regions = regions if regions is not None else REGIONS
        self.cell_side = cell_side
        self.cell_gap = cell_gap
        self.panel_padding = panel_padding
        self.regions = regions
        self.title_font_size = title_font_size
        self.show_offsets = show_offsets
        self.cells: Dict[int, MemoryByteCell] = {}
        self.panels: Dict[str, Rectangle] = {}
        self.titles: Dict[str, Text] = {}
        self.size_tags: Dict[str, Text] = {}

        self._build()

    # -- construction ----------------------------------------------------

    def _cell_x(self, offset: int) -> float:
        """X coordinate of a cell's center in local coordinates."""
        return (
            -self.total_cells_width() / 2
            + self.cell_side / 2
            + offset * (self.cell_side + self.cell_gap)
        )

    def total_cells_width(self) -> float:
        """Width of the cell row, excluding panel padding."""
        n = config.TOTAL_MEMORY_SIZE
        return n * self.cell_side + (n - 1) * self.cell_gap

    def _build(self) -> None:
        for region in self.regions:
            panel_width = (
                region.size * self.cell_side
                + (region.size - 1) * self.cell_gap
                + 2 * self.panel_padding
            )
            center_x = (
                self._cell_x(region.offset)
                + (region.size - 1) * (self.cell_side + self.cell_gap) / 2
            )
            region_group = LabeledMemoryRegion(
                name=region.name,
                size=region.size,
                color=region.color,
                width=panel_width,
                height=self.cell_side + 0.4,
                title_font_size=self.title_font_size,
            )
            region_group.move_to(np.array([center_x, 0.0, 0.0]))
            self.add(region_group)
            self.panels[region.name] = region_group.panel
            self.titles[region.name] = region_group.title
            self.size_tags[region.name] = region_group.size_tag

        for offset in range(config.TOTAL_MEMORY_SIZE):
            cell = MemoryByteCell(
                offset=offset if self.show_offsets else None,
                side_length=self.cell_side,
            )
            cell.shift(RIGHT * self._cell_x(offset))
            self.add(cell)
            self.cells[offset] = cell

    # -- accessors -------------------------------------------------------

    def cell(self, offset: int) -> MemoryByteCell:
        """The byte cell at ``offset`` (raises KeyError if unknown)."""
        return self.cells[offset]

    def panel(self, name: str) -> Rectangle:
        """The region panel for ``name``."""
        return self.panels[name]

    def title(self, name: str) -> Text:
        """The region title text for ``name``."""
        return self.titles[name]

    def cell_center(self, offset: int) -> np.ndarray:
        """Center point of the cell at ``offset`` (for animations)."""
        return self.cells[offset].get_center()

    # -- content ---------------------------------------------------------

    def set_byte(self, offset: int, value: int) -> "MemoryLayout":
        """Show ``value`` in the cell at ``offset``."""
        self.cells[offset].set_value(value)
        return self

    def set_bytes(self, values: List[int]) -> "MemoryLayout":
        """Show every byte of ``values`` (length must equal
        TOTAL_MEMORY_SIZE)."""
        if len(values) != config.TOTAL_MEMORY_SIZE:
            raise ValueError(
                f"expected {config.TOTAL_MEMORY_SIZE} bytes, got {len(values)}"
            )
        for offset, value in enumerate(values):
            self.set_byte(offset, value)
        return self

    def clear(self) -> "MemoryLayout":
        """Hide all cell characters (empty model state)."""
        for cell in self.cells.values():
            cell.clear()
        return self


class BoundaryMarker(VGroup):
    """The "LOGICAL BUFFER ENDS HERE" boundary marker: a vertical bar
    with direction ticks and a monospaced label.

    Use ``place_between`` to align it between two cells without
    hardcoding coordinates.
    """

    def __init__(
        self,
        height: float = 2.6,
        bar_width: float = 0.06,
        label: str = "LOGICAL BUFFER ENDS HERE",
        font_size: int = 15,
        color: str = config.COLOR_WARNING,
    ) -> None:
        super().__init__()
        self.bar = Rectangle(
            width=bar_width,
            height=height,
            fill_color=color,
            fill_opacity=0.85,
            stroke_color=color,
            stroke_width=1,
        )
        tick_size = bar_width * 1.6
        self.ticks = VGroup(
            Triangle(color=color, fill_opacity=0.85).scale(tick_size),
            Triangle(color=color, fill_opacity=0.85).scale(tick_size).rotate(
                np.pi
            ),
        )
        self.ticks[0].next_to(self.bar, LEFT, buff=0.0)
        self.ticks[1].next_to(self.bar, RIGHT, buff=0.0)
        self.label = _mono_text(label, font_size=font_size, color=color)
        self.label.next_to(self.bar, RIGHT, buff=0.25)
        self.add(self.bar, self.ticks, self.label)

    def place_between(
        self,
        left_mobject: "MemoryByteCell",
        right_mobject: "MemoryByteCell",
        y: Optional[float] = None,
    ) -> "BoundaryMarker":
        """Center the marker's BAR between two cell centers, keeping
        its current height; optionally fix its Y position.

        The bar is the anchor (not the whole group): the label may
        extend far to one side and must not drag the bar off its
        boundary position.
        """
        midpoint = (left_mobject.get_center() + right_mobject.get_center()) / 2
        self.shift(midpoint - self.bar.get_center())
        if y is not None:
            self.shift(UP * (y - self.bar.get_center()[1]))
        return self


class MemoryDumpRow(VGroup):
    """One row of the hex dump: offset, hex byte, ASCII character.

    Columns use fixed gaps and the monospaced font, so identical
    strings align across rows automatically.
    """

    def __init__(self, offset: int, value: int, font_size: int = 20) -> None:
        super().__init__()
        self.offset = offset
        self.value = value
        self.offset_text = _mono_text(f"{offset:02d}", font_size=font_size)
        self.hex_text = _mono_text(hex_byte(value), font_size=font_size)
        self.char_text = _mono_text(ascii_char(value), font_size=font_size)
        self.hex_text.next_to(self.offset_text, RIGHT, buff=1.1)
        self.char_text.next_to(self.hex_text, RIGHT, buff=1.1)
        self.add(self.offset_text, self.hex_text, self.char_text)

    def set_value(self, value: int) -> "MemoryDumpRow":
        """Update the hex and ASCII cells of this row."""
        self.value = value
        self.hex_text.text = hex_byte(value)
        self.char_text.text = ascii_char(value)
        return self


class HexDumpTable(VGroup):
    """A complete dump table (header + one row per byte), generated
    from a list of byte values. Rows are aligned column-wise and the
    table can be animated as a whole."""

    def __init__(
        self,
        values: List[int],
        start_offset: int = 0,
        font_size: int = 20,
        include_header: bool = True,
    ) -> None:
        super().__init__()
        self.rows: List[MemoryDumpRow] = []
        for i, value in enumerate(values):
            self.rows.append(
                MemoryDumpRow(start_offset + i, value, font_size=font_size)
            )
        body = VGroup(*self.rows).arrange(DOWN, buff=0.18)
        if include_header:
            self.header = VGroup(
                _mono_text("OFFSET", font_size=font_size, color=config.COLOR_OFFSET_LABEL),
                _mono_text("HEX", font_size=font_size, color=config.COLOR_OFFSET_LABEL),
                _mono_text("ASCII", font_size=font_size, color=config.COLOR_OFFSET_LABEL),
            )
            self.header[1].next_to(self.header[0], RIGHT, buff=1.1)
            self.header[2].next_to(self.header[1], RIGHT, buff=1.1)
            self.header.next_to(body, UP, buff=0.3)
            self.add(self.header, body)
        else:
            self.header = None
            self.add(body)

    def highlight_rows(self, offsets: List[int], color: str = config.COLOR_WARNING):
        """Recolor the rows for the given absolute offsets."""
        for row in self.rows:
            if row.offset in offsets:
                for text in (row.offset_text, row.hex_text, row.char_text):
                    text.set_color(color)
        return self


class StatusLabel(VGroup):
    """A status line with a drawn symbol: a check for FITS, a warning
    triangle for BOUNDARY CROSSED.

    The symbol is drawn geometry (not a font glyph) so it renders
    identically on every system; color is never the only signal.
    """

    def __init__(
        self,
        text: str,
        fits: bool,
        font_size: int = 40,
        symbol_size: float = 0.35,
    ) -> None:
        super().__init__()
        self.text = Text(
            text, font=config.FONT_SANS, font_size=font_size,
            color=config.COLOR_SAFE if fits else config.COLOR_WARNING,
        )
        if fits:
            self.symbol = VGroup(
                Line(ORIGIN, np.array([0.22, 0.10, 0.0])),
                Line(np.array([0.22, 0.10, 0.0]), np.array([0.42, -0.16, 0.0])),
            )
            self.symbol.set_stroke(config.COLOR_SAFE, width=6)
        else:
            self.symbol = Triangle(
                color=config.COLOR_WARNING, fill_opacity=0.9
            ).scale(symbol_size)
        self.symbol.move_to(ORIGIN)
        self.text.next_to(self.symbol, RIGHT, buff=0.25)
        self.add(self.symbol, self.text)