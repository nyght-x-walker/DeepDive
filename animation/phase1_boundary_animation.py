"""Phase 1 animation: Seeing the Boundary.

All eight scenes (film order):

1. OpeningScene
2. ByteRepresentationScene
3. MemoryLayoutScene
4. SafeInputScene
5. BoundaryCrossingScene
6. HexDumpScene
7. SafeModelClarificationScene
8. PhaseTransitionScene

Render the complete film with, e.g.:

    uv run manim render -ql --media_dir renders \\
        animation/phase1_boundary_animation.py FullFilm

Render previews with, e.g.:

    uv run manim render -ql --media_dir renders \\
        animation/phase1_boundary_animation.py OpeningScene
"""

from manim import (
    Arc,
    Arrow,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    Group,
    GrowFromCenter,
    LaggedStart,
    LEFT,
    Line,
    ORIGIN,
    Rectangle,
    RIGHT,
    Scene,
    Square,
    Text,
    Triangle,
    UP,
    ValueTracker,
    VGroup,
    Write,
    config as manim_config,
)

from animation import config as cfg
from animation.components import (
    BoundaryMarker,
    HexDumpTable,
    MemoryLayout,
    StatusLabel,
    build_memory,
    hex_byte,
    input_length,
    string_to_bytes,
)

# Final output target: 1920x1080, 60 fps. Only force full resolution
# at high quality so the -ql/-qm preview workflow stays cheap.
manim_config.background_color = cfg.COLOR_BACKGROUND
if manim_config.quality in ("high", "very_high"):
    manim_config.pixel_height = 1080
    manim_config.pixel_width = 1920
    manim_config.frame_rate = 60


def _text(text, font_size, color=cfg.COLOR_TEXT, font=cfg.FONT_SANS):
    """Shortcut for readable sans-serif text."""
    return Text(text, font=font, font_size=font_size, color=color)


def _mono(text, font_size, color=cfg.COLOR_TEXT):
    """Shortcut for monospaced byte/hex/offset text."""
    return Text(text, font=cfg.FONT_MONO, font_size=font_size, color=color)


# ---------------------------------------------------------------------------
# Pacing: per-scene targets from docs/phase1_audio_timing_plan.md (the
# approved visual durations for the recorded narration).
# Sum 581 s = 9:41 — deviation from the 6-8 minute nominal target was
# accepted with the audio timing plan (Section 5).
# ---------------------------------------------------------------------------

SCENE_TARGETS = {
    "OpeningScene": 42,
    "ByteRepresentationScene": 65,
    "MemoryLayoutScene": 76,
    "SafeInputScene": 60,
    "BoundaryCrossingScene": 100,
    "HexDumpScene": 84,
    "SafeModelClarificationScene": 88,
    "PhaseTransitionScene": 66,
}

# Film-level dissolve between scenes; accounted for by _pad_to so every
# scene lands exactly on its target.
FADE_DURATION = 0.8


def _mark_scene_start(scene) -> None:
    """Record the start of a scene (film runs several scenes in one
    Scene instance, so timing must be relative to the scene start)."""
    scene._scene_start = scene.time


def _pad_to(scene, target: float) -> None:
    """Extend the scene's final hold so its total on-screen time
    reaches ``target`` seconds (narration-length pause)."""
    remaining = target - (scene.time - scene._scene_start) - FADE_DURATION
    if remaining > 0.25:
        scene.wait(remaining)


def _scene_fade_out(scene) -> None:
    """Dissolve everything on screen: the film-level transition."""
    if scene.mobjects:
        scene.play(
            FadeOut(Group(*scene.mobjects)),
            run_time=FADE_DURATION,
        )


# ---------------------------------------------------------------------------
# Scene 1: OpeningScene
# ---------------------------------------------------------------------------


class OpeningScene(Scene):
    """Title, subtitle, and the security question. No decorative
    hacker imagery; the question itself establishes relevance."""

    def construct(self):
        _mark_scene_start(self)
        title = _text("Seeing the Boundary", font_size=64)
        title.to_edge(UP, buff=1.6)

        subtitle = _text(
            "Visualizing Logical Memory Regions in C++",
            font_size=32,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        subtitle.next_to(title, DOWN, buff=0.35)

        question = _text(
            "When does an input become bigger than the box it is written into?",
            font_size=28,
            color=cfg.COLOR_INPUT,
        )
        question.next_to(subtitle, DOWN, buff=0.9)

        self.play(Write(title))
        self.wait(3.5)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(3.5)
        self.play(FadeIn(question, shift=UP * 0.2))
        self.wait(5)

        # Pin the question as a persistent top caption for the film.
        self.play(
            question.animate.scale(0.75).to_edge(UP, buff=0.35)
        )
        self.wait(7)
        _pad_to(self, SCENE_TARGETS["OpeningScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# Scene 2: ByteRepresentationScene
# ---------------------------------------------------------------------------


class ByteRepresentationScene(Scene):
    """One byte in three forms — binary, hexadecimal, ASCII — and the
    relationship between them: each hex digit is one 4-bit nibble."""

    def construct(self):
        _mark_scene_start(self)
        header = _text("One byte = 8 bits", font_size=36)
        header.to_edge(UP, buff=0.8)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(2)

        # --- binary row --------------------------------------------------
        nibble1 = [_mono(bit, font_size=44, color=cfg.COLOR_INPUT if bit == "1" else cfg.COLOR_TEXT)
                   for bit in "0100"]
        nibble2 = [_mono(bit, font_size=44, color=cfg.COLOR_INPUT if bit == "1" else cfg.COLOR_TEXT)
                   for bit in "0001"]
        gap = _mono("  ", font_size=44)
        bits = (
            VGroup(*nibble1).arrange(RIGHT, buff=0.12)
        )
        bits2 = VGroup(*nibble2).arrange(RIGHT, buff=0.12)
        binary_row = VGroup(bits, gap, bits2).arrange(RIGHT, buff=0.08)
        binary_row.move_to(ORIGIN).shift(UP * 1.5)
        binary_label = _text("binary", font_size=24, color=cfg.COLOR_OFFSET_LABEL)
        binary_label.next_to(binary_row, DOWN, buff=0.15)

        self.play(
            LaggedStart(
                *[FadeIn(bit, scale=0.5) for bit in binary_row],
                lag_ratio=0.15,
                run_time=5,
            )
        )
        self.play(FadeIn(binary_label))
        self.wait(4)

        # --- nibble underlines -> hex digits ------------------------------
        under1 = Line(LEFT, RIGHT, color=cfg.COLOR_CELL_STROKE, stroke_width=4)
        under1.set_width(bits.width)
        under1.move_to(bits.get_bottom() + DOWN * 0.75)
        under2 = under1.copy().move_to(bits2.get_bottom() + DOWN * 0.75)

        digit1 = _mono("4", font_size=40, color=cfg.COLOR_INPUT)
        digit1.next_to(under1, DOWN, buff=0.15)
        digit2 = _mono("1", font_size=40, color=cfg.COLOR_INPUT)
        digit2.next_to(under2, DOWN, buff=0.15)
        digits = VGroup(digit1, digit2)

        self.play(Create(under1), Create(under2))
        self.play(FadeIn(digit1), FadeIn(digit2))
        self.wait(4.5)

        # --- hexadecimal label ---------------------------------------------
        hex_label = _mono("0x41", font_size=40, color=cfg.COLOR_INPUT)
        hex_label.next_to(digits, DOWN, buff=0.35)
        hex_caption = _text("hexadecimal", font_size=24, color=cfg.COLOR_OFFSET_LABEL)
        hex_caption.next_to(hex_label, DOWN, buff=0.1)
        arrow1 = Arrow(digits.get_bottom(), hex_label.get_top(), color=cfg.COLOR_CELL_STROKE)
        self.play(FadeIn(arrow1), FadeIn(hex_label), FadeIn(hex_caption))
        self.wait(5)

        # --- ASCII ----------------------------------------------------------
        ascii_cell = Square(
            side_length=1.0,
            fill_color=cfg.COLOR_CELL_FILL,
            fill_opacity=1.0,
            stroke_color=cfg.COLOR_INPUT,
            stroke_width=3,
        )
        ascii_char = _mono("A", font_size=56, color=cfg.COLOR_INPUT)
        ascii_char.move_to(ascii_cell.get_center())
        ascii_group = VGroup(ascii_cell, ascii_char)
        ascii_group.next_to(hex_label, RIGHT, buff=1.2)

        ascii_caption = _text("ASCII", font_size=24, color=cfg.COLOR_OFFSET_LABEL)
        ascii_caption.next_to(ascii_group, DOWN, buff=0.15)
        arrow2 = Arrow(hex_label.get_right(), ascii_group.get_left(), color=cfg.COLOR_CELL_STROKE)

        self.play(FadeIn(arrow2))
        self.play(GrowFromCenter(ascii_cell), FadeIn(ascii_char), FadeIn(ascii_caption))
        self.wait(6)

        # --- summary --------------------------------------------------------
        summary = _mono("0100 0001  =  0x41  =  'A'", font_size=30, color=cfg.COLOR_TEXT)
        summary.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(summary, shift=UP * 0.3))
        self.wait(9)
        _pad_to(self, SCENE_TARGETS["ByteRepresentationScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# Scene 3: MemoryLayoutScene
# ---------------------------------------------------------------------------


class MemoryLayoutScene(Scene):
    """Build the contiguous 20-byte model and divide it into the three
    logical regions: buffer[8], criticalFlag, buffer2[8]."""

    def construct(self):
        _mark_scene_start(self)
        header = _text("One contiguous array: 20 bytes", font_size=32)
        header.to_edge(UP, buff=0.6)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(2.5)

        layout = MemoryLayout()
        layout.to_edge(UP, buff=1.9)

        # 1. Build the three logical regions, in physical order.
        for name in ("buffer", "criticalFlag", "buffer2"):
            self.play(
                FadeIn(layout.panel(name)),
                FadeIn(layout.title(name)),
                FadeIn(layout.size_tags[name]),
                run_time=2.0,
            )
            self.wait(2.5)

        # 2. Show the byte cells with their offsets.
        self.play(
            LaggedStart(
                *[FadeIn(layout.cell(i)) for i in range(20)],
                lag_ratio=0.03,
                run_time=6,
            )
        )
        self.wait(6.5)

        # 3. Bracket: the cells are one array.
        bracket = Line(
            layout.cell(0).get_bottom() + DOWN * 0.45,
            layout.cell(19).get_bottom() + DOWN * 0.45,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        array_note = _text(
            "one std::array of 20 bytes",
            font_size=22,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        array_note.next_to(bracket, DOWN, buff=0.12)
        self.play(Create(bracket), FadeIn(array_note), run_time=2.0)
        self.wait(6)

        # 4. Disclaimer: this is an educational model.
        disclaimer = _text(
            "Educational contiguous model — not a real stack-frame layout.",
            font_size=24,
            color=cfg.COLOR_WARNING,
        )
        disclaimer.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(disclaimer, shift=UP * 0.2), run_time=2.0)
        self.wait(10)
        _pad_to(self, SCENE_TARGETS["MemoryLayoutScene"])
        _scene_fade_out(self)

# ---------------------------------------------------------------------------
# Scene 4: SafeInputScene
# ---------------------------------------------------------------------------


class SafeInputScene(Scene):
    """HELLO (5 bytes) fits the logical buffer: 00..04 get the input,
    cells 05..07 stay empty, and flag + buffer2 remain untouched.

    Narration (docs/phase1_narration.md, Scene 4): "The first input is
    HELLO: five bytes. The logical buffer holds eight. Five is smaller
    than eight, so every byte lands inside the buffer and the adjacent
    regions are untouched. Input length and buffer capacity are
    different quantities — here, capacity wins."
    """

    def construct(self):
        _mark_scene_start(self)
        text = cfg.SAFE_INPUT

        header = _text(f"INPUT: {text}", font_size=32)
        header.to_edge(UP, buff=0.6)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(2)

        # Fresh array with the program's initial contents
        # (src/phase1_boundary_model.cpp:109-121): SAFE, zero flag bytes,
        # SECURE. Cells 04..07 are shown empty so the unused buffer
        # capacity reads clearly (program value is 0x00 = '.' in dumps).
        layout = MemoryLayout()
        layout.to_edge(UP, buff=1.9)
        for i, char in enumerate(cfg.INITIAL_BUFFER):
            layout.set_byte(i, ord(char))
        for i in range(len(cfg.INITIAL_BUFFER), cfg.BUFFER_SIZE):
            layout.cell(i).clear()
        for i in range(cfg.FLAG_OFFSET, cfg.FLAG_OFFSET + cfg.FLAG_SIZE):
            layout.set_byte(i, 0)
        for i, char in enumerate(cfg.INITIAL_SECOND_BUFFER):
            layout.set_byte(cfg.SECOND_BUFFER_OFFSET + i, ord(char))
        for i in range(cfg.SECOND_BUFFER_OFFSET + len(cfg.INITIAL_SECOND_BUFFER),
                       cfg.TOTAL_MEMORY_SIZE):
            layout.set_byte(i, 0)
        self.play(FadeIn(layout), run_time=1.2)
        self.wait(2.5)

        # Narration: "Input length and buffer capacity are different
        # quantities — here, capacity wins."
        info_input = _text(
            f"Input size: {input_length(text)} bytes",
            font_size=24,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        info_buffer = _text(
            f"Logical buffer size: {cfg.BUFFER_SIZE} bytes",
            font_size=24,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        info_input.move_to([-3.7, -1.5, 0.0])
        info_buffer.move_to([3.9, -1.5, 0.0])
        self.play(FadeIn(info_input), FadeIn(info_buffer))
        self.wait(2)

        # Narration: "H, E, L, L, O fly into cells 00..04 one by one."
        self.play(
            LaggedStart(
                *[
                    FadeIn(layout.cell(i).char_text, scale=2.0, shift=UP * 0.35)
                    for i in range(len(text))
                ],
                lag_ratio=0.35,
                run_time=3.5,
            )
        )
        self.wait(3.5)

        # Cells 05..07 remain visibly empty (requirement: show the
        # remaining buffer capacity clearly).
        unused = _text("3 bytes unused", font_size=17, color=cfg.COLOR_OFFSET_LABEL)
        unused.move_to([layout.cell(6).get_center()[0], -1.0, 0.0])
        self.play(FadeIn(unused))
        self.wait(2)

        # Hex values derived from the byte model, never hardcoded.
        legend = _mono(
            f"{text} = "
            + " ".join(f"0x{hex_byte(b)}" for b in string_to_bytes(text)),
            font_size=26,
            color=cfg.COLOR_INPUT,
        )
        legend.move_to([0.0, -2.3, 0.0])
        self.play(FadeIn(legend, shift=UP * 0.2))
        self.wait(2.5)

        # Narration: "the flag and buffer2 briefly flash to confirm
        # they were not touched."
        tags = {
            "criticalFlag": "flag: unchanged",
            "buffer2": "buffer2: unchanged",
        }
        for name, caption in tags.items():
            panel = layout.panel(name)
            tag = _text(caption, font_size=17, color=cfg.COLOR_OFFSET_LABEL)
            tag.move_to([panel.get_center()[0], -1.1, 0.0])
            self.play(
                panel.animate.set_fill(opacity=0.32),
                FadeIn(tag),
                run_time=0.4,
            )
            self.play(panel.animate.set_fill(opacity=0.16), run_time=0.4)
        self.wait(0.5)

        # Narration: "The status panel pops in: FITS."
        status = StatusLabel("Status: FITS", fits=True, font_size=30)
        status.move_to([0.0, -3.3, 0.0])
        self.play(GrowFromCenter(status))
        self.wait(6)
        _pad_to(self, SCENE_TARGETS["SafeInputScene"])
        _scene_fade_out(self)

        # Transition (film level): HELLO fades and the grid returns to
        # its initial state for the next input — the program builds a
        # fresh array for each demonstration.


# ---------------------------------------------------------------------------
# Scene 5: BoundaryCrossingScene
# ---------------------------------------------------------------------------


class BoundaryCrossingScene(Scene):
    """ABCDEFGHIJKLMNO (15 bytes) exceeds the logical buffer by 7:
    A..H land in 00..07, then I..O continue into the adjacent logical
    regions (flag 08..11, buffer2 12..14) inside the safe model only.

    Narration (docs/phase1_narration.md, Scene 5): "Now the input is
    fifteen bytes: A through O. Fifteen is larger than eight. The first
    eight bytes fit inside the logical buffer — and then the boundary
    ends. In this deliberately constructed model, the remaining bytes
    appear in adjacent logical regions: the critical flag and the
    second buffer. ... When the input exceeds the boundary, the
    additional bytes may overwrite adjacent data in an unsafe real-world
    implementation."
    """

    def construct(self):
        _mark_scene_start(self)
        text = cfg.OVERSIZED_INPUT

        header = _text(f"INPUT: {text}", font_size=32)
        header.to_edge(UP, buff=0.6)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(2.5)

        # Fresh array, same initial contents as SafeInputScene.
        layout = MemoryLayout()
        layout.to_edge(UP, buff=1.9)
        for i, char in enumerate(cfg.INITIAL_BUFFER):
            layout.set_byte(i, ord(char))
        for i in range(len(cfg.INITIAL_BUFFER), cfg.BUFFER_SIZE):
            layout.cell(i).clear()
        for i in range(cfg.FLAG_OFFSET, cfg.FLAG_OFFSET + cfg.FLAG_SIZE):
            layout.set_byte(i, 0)
        for i, char in enumerate(cfg.INITIAL_SECOND_BUFFER):
            layout.set_byte(cfg.SECOND_BUFFER_OFFSET + i, ord(char))
        for i in range(cfg.SECOND_BUFFER_OFFSET + len(cfg.INITIAL_SECOND_BUFFER),
                       cfg.TOTAL_MEMORY_SIZE):
            layout.set_byte(i, 0)
        self.play(FadeIn(layout), run_time=1.2)
        self.wait(3)

        # Narration: "Input length and buffer capacity are different
        # quantities." Physical vs logical distinction (requirement):
        # the gray line spans the whole contiguous array; the red marker
        # will show where the logical buffer ends.
        info_input = _text(
            f"Input size: {input_length(text)} bytes",
            font_size=24,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        info_buffer = _text(
            f"Logical buffer size: {cfg.BUFFER_SIZE} bytes",
            font_size=24,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        info_input.move_to([-3.7, -1.5, 0.0])
        info_buffer.move_to([3.9, -1.5, 0.0])
        self.play(FadeIn(info_input), FadeIn(info_buffer), run_time=1.5)

        physical_line = Line(
            layout.cell(0).get_bottom() + DOWN * 0.45,
            layout.cell(19).get_bottom() + DOWN * 0.45,
            color=cfg.COLOR_CELL_STROKE,
        )
        tag_physical = _text(
            "physical: 20 contiguous bytes",
            font_size=17,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        tag_physical.move_to([-4.2, -0.9, 0.0])
        tag_logical = _text(
            "logical: region ownership",
            font_size=17,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        tag_logical.move_to([4.2, -0.9, 0.0])
        self.play(Create(physical_line), FadeIn(tag_physical), FadeIn(tag_logical), run_time=1.5)
        self.wait(3)

        # Narration: "The first eight bytes fit inside the logical
        # buffer" — A..H land in cells 00..07 one by one.
        self.play(
            LaggedStart(
                *[
                    FadeIn(layout.cell(i).char_text, scale=2.0, shift=UP * 0.35)
                    for i in range(cfg.BUFFER_SIZE)
                ],
                lag_ratio=0.3,
                run_time=6.5,
            )
        )
        self.wait(6.5)  # pause clearly at the logical boundary

        # Narration: "and then the boundary ends." The red marker bar
        # between cells 07 and 08: LOGICAL BUFFER ENDS HERE.
        marker = BoundaryMarker(height=1.7, font_size=16)
        marker.place_between(layout.cell(7), layout.cell(8))
        marker.label.next_to(marker.bar, UP, buff=0.08)
        # Keep the label clear of the flag column's title + size-tag stack.
        floor = layout.size_tags["criticalFlag"].get_top()[1] + 0.06
        if marker.label.get_bottom()[1] < floor:
            marker.label.shift(UP * (floor - marker.label.get_bottom()[1]))
        self.play(FadeIn(marker, shift=UP * 0.4), run_time=1.5)
        self.wait(6)

        # Narration: "the remaining bytes appear in adjacent logical
        # regions: the critical flag and the second buffer."
        self.play(
            LaggedStart(
                *[
                    FadeIn(layout.cell(i).char_text, scale=2.0, shift=UP * 0.35)
                    for i in range(cfg.FLAG_OFFSET, cfg.FLAG_OFFSET + cfg.FLAG_SIZE)
                ],
                lag_ratio=0.3,
                run_time=4,
            )
        )
        self.play(
            layout.panel("criticalFlag").animate.set_fill(opacity=0.32),
            run_time=0.5,
        )
        self.play(layout.panel("criticalFlag").animate.set_fill(opacity=0.16), run_time=0.5)
        self.wait(4)

        self.play(
            LaggedStart(
                *[
                    FadeIn(layout.cell(i).char_text, scale=2.0, shift=UP * 0.35)
                    for i in range(12, 15)
                ],
                lag_ratio=0.3,
                run_time=3.5,
            )
        )
        self.play(
            layout.panel("buffer2").animate.set_fill(opacity=0.32),
            run_time=0.5,
        )
        self.play(layout.panel("buffer2").animate.set_fill(opacity=0.16), run_time=0.5)
        self.wait(3.5)

        # Narration: "The excess counter counts up to 7."
        excess_tracker = ValueTracker(0)
        excess_text = _text(
            "Excess: 0 bytes",
            font_size=24,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        excess_text.move_to([0.0, -2.2, 0.0])

        def _update_excess(mobj):
            count = int(excess_tracker.get_value())
            mobj.text = f"Excess: {count} bytes"
            mobj.set_color(
                cfg.COLOR_WARNING if count > 0 else cfg.COLOR_OFFSET_LABEL
            )

        excess_text.add_updater(_update_excess)
        self.play(FadeIn(excess_text), run_time=1.5)
        self.play(excess_tracker.animate.set_value(7), run_time=3)
        excess_text.clear_updaters()
        self.wait(3)

        # Narration: "Status flips to BOUNDARY CROSSED."
        status = StatusLabel("Status: BOUNDARY CROSSED", fits=False, font_size=26)
        status.move_to([0.0, -2.95, 0.0])
        self.play(GrowFromCenter(status), run_time=1.5)
        self.wait(6)

        # Safe-model statement (mandated phrasing, AGENTIC.md).
        statement = _text(
            "Educational model: no actual out-of-bounds write.",
            font_size=22,
            color=cfg.COLOR_WARNING,
        )
        statement.scale_to_fit_width(12.4)
        statement.move_to([0.0, -3.7, 0.0])
        self.play(FadeIn(statement, shift=UP * 0.2), run_time=1.5)
        self.wait(9)
        _pad_to(self, SCENE_TARGETS["BoundaryCrossingScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# Scene 6: HexDumpScene
# ---------------------------------------------------------------------------


class HexDumpScene(Scene):
    """Read the 15-byte input as a dump — offset, hex, ASCII — in the
    C++ program's own format. Grows out of the memory-cell view.

    Narration (docs/phase1_narration.md, Scene 6): "The same memory,
    read as data: offsets on the left, each byte in hexadecimal, and
    its ASCII meaning on the right. A is 0x41, J is 0x4a, O is 0x4f.
    The dump makes the crossing explicit — the flag cells at offsets
    eight through eleven are no longer zeros; they now hold the bytes
    I, J, K and L."
    """

    def construct(self):
        _mark_scene_start(self)
        values = build_memory(cfg.OVERSIZED_INPUT)

        # 1. The memory-cell view of the oversized input.
        layout = MemoryLayout()
        layout.to_edge(UP, buff=1.5)
        layout.set_bytes(values)
        header = _text("The same memory, read as data", font_size=32)
        header.to_edge(UP, buff=0.5)
        self.play(FadeIn(layout), FadeIn(header, shift=DOWN * 0.2))
        self.wait(3.5)

        # 2. Short explanation of the three dump columns.
        explain = VGroup(
            _text(
                "offset — the position of each byte (00..19)",
                font_size=17,
                color=cfg.COLOR_OFFSET_LABEL,
            ),
            _text(
                "hexadecimal — one byte as two hex digits (41..4f)",
                font_size=17,
                color=cfg.COLOR_OFFSET_LABEL,
            ),
            _text(
                "ASCII — the printable character for a byte",
                font_size=17,
                color=cfg.COLOR_OFFSET_LABEL,
            ),
        ).arrange(DOWN, buff=0.5)
        explain.move_to([0.0, -2.4, 0.0])
        self.play(
            LaggedStart(
                *[FadeIn(line, shift=UP * 0.2) for line in explain],
                lag_ratio=0.5,
                run_time=4,
            )
        )
        self.wait(6)

        # 3. The strip shrinks to the top; the dump grows below it.
        self.play(FadeOut(explain), FadeOut(header))
        self.play(layout.animate.scale(0.4).to_edge(UP, buff=0.5), run_time=1.8)
        self.wait(3)

        table_header = VGroup(
            _mono("OFFSET", font_size=18, color=cfg.COLOR_OFFSET_LABEL),
            _mono("HEX", font_size=18, color=cfg.COLOR_OFFSET_LABEL),
            _mono("ASCII", font_size=18, color=cfg.COLOR_OFFSET_LABEL),
        )
        table_header[1].next_to(table_header[0], RIGHT, buff=1.1)
        table_header[2].next_to(table_header[1], RIGHT, buff=1.1)
        table_header.move_to([0.0, 1.79, 0.0])

        caption = _text(
            "Every byte, one address at a time.",
            font_size=18,
            color=cfg.COLOR_OFFSET_LABEL,
        )
        caption.move_to([0.0, -3.6, 0.0])

        self.play(FadeIn(table_header), FadeIn(caption, shift=UP * 0.2))
        self.wait(4)

        # 4. Page 1: rows 00..07, the logical buffer[8] (blue).
        page1 = HexDumpTable(values[:8], start_offset=0, font_size=18)
        page1.highlight_rows(range(8), color=cfg.COLOR_BUFFER)
        page1.move_to([0.0, -0.1, 0.0])
        tag_buffer = _text(
            "buffer[8]", font_size=16, color=cfg.COLOR_BUFFER,
            font=cfg.FONT_MONO,
        )
        tag_buffer.move_to(
            [page1.get_left()[0] - 0.6, page1.rows[0].get_center()[1], 0.0]
        )

        self.play(
            LaggedStart(
                *[FadeIn(row, shift=UP * 0.15) for row in page1.rows],
                lag_ratio=0.12,
                run_time=4.5,
            ),
            FadeIn(tag_buffer),
        )
        self.wait(6)

        # 5. Page 2: rows 08..14, the adjacent logical regions.
        page2 = HexDumpTable(values[8:15], start_offset=8, font_size=18)
        page2.highlight_rows(range(8, 12), color=cfg.COLOR_FLAG)
        page2.highlight_rows(range(12, 15), color=cfg.COLOR_SECOND_BUFFER)
        page2.move_to([0.0, -0.1, 0.0])
        tag_flag = _text("flag", font_size=16, color=cfg.COLOR_FLAG, font=cfg.FONT_MONO)
        tag_flag.move_to(
            [page2.get_left()[0] - 0.6,
             (page2.rows[0].get_center()[1] + page2.rows[3].get_center()[1]) / 2,
             0.0]
        )
        tag_buffer2 = _text(
            "buffer2", font_size=16, color=cfg.COLOR_SECOND_BUFFER,
            font=cfg.FONT_MONO,
        )
        tag_buffer2.move_to(
            [page2.get_left()[0] - 0.6,
             (page2.rows[4].get_center()[1] + page2.rows[6].get_center()[1]) / 2,
             0.0]
        )

        self.play(FadeOut(page1, shift=LEFT * 0.3), FadeOut(tag_buffer))
        self.play(
            LaggedStart(
                *[FadeIn(row, shift=UP * 0.15) for row in page2.rows],
                lag_ratio=0.12,
                run_time=4,
            ),
            FadeIn(tag_flag),
            FadeIn(tag_buffer2),
        )
        self.wait(6)

        # 6. The flag cells are no longer zeros.
        flag_note = _text(
            "offsets 08..11: flag cells now hold I, J, K, L",
            font_size=17,
            color=cfg.COLOR_FLAG,
        )
        flag_note.move_to([0.0, -3.2, 0.0])
        self.play(FadeIn(flag_note, shift=UP * 0.2), run_time=1.5)
        self.wait(12)
        _pad_to(self, SCENE_TARGETS["HexDumpScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# Scene 7: SafeModelClarificationScene
# ---------------------------------------------------------------------------


class SafeModelClarificationScene(Scene):
    """Left/right split: the safe educational model vs the next
    phase's real vulnerable operation. No exploit is executed or
    animated; no ROP or return-address content.

    Narration (docs/phase1_narration.md, Scene 7): "Let us be precise.
    Phase 1 did not perform an actual out-of-bounds write. The program
    caps the copy at the total array size, so every byte stayed inside
    the twenty-byte model. This is a safe visualization of where bytes
    would land. An actual out-of-bounds access in C++ is undefined
    behavior — the compiler is allowed to do anything, and the program
    may not be reliable at all."
    """

    def construct(self):
        _mark_scene_start(self)
        header = _text("Phase 1 is a safe visualization", font_size=32)
        header.to_edge(UP, buff=0.6)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(4)

        # --- LEFT panel: safe educational model -------------------------
        left_panel = Rectangle(
            width=6.4,
            height=5.6,
            fill_color=cfg.COLOR_SAFE,
            fill_opacity=0.05,
            stroke_color=cfg.COLOR_SAFE,
            stroke_width=2,
        )
        left_panel.move_to([-3.75, -0.6, 0.0])
        left_title = _text(
            "Safe educational model", font_size=24, color=cfg.COLOR_SAFE
        )
        left_title.scale_to_fit_width(6.0)
        left_title.move_to([-3.75, 1.75, 0.0])

        left_statements = [
            "one contiguous\nstd::array of 20 bytes",
            "copy capped at the\ntotal array size (std::min)",
            "no actual out-of-bounds\nwrite occurred",
            "not a compiler-generated\nstack frame",
        ]

        # --- RIGHT panel: next phase ------------------------------------
        right_panel = Rectangle(
            width=6.4,
            height=5.6,
            fill_color=cfg.COLOR_WARNING,
            fill_opacity=0.05,
            stroke_color=cfg.COLOR_WARNING,
            stroke_width=2,
        )
        right_panel.move_to([3.75, -0.6, 0.0])
        right_title = _text(
            "Next phase:\nreal vulnerable operation",
            font_size=24,
            color=cfg.COLOR_WARNING,
        )
        right_title.scale_to_fit_width(6.0)
        right_title.move_to([3.75, 1.75, 0.0])

        right_statements = [
            "actual vulnerable\nstrcpy operation",
            "a real out-of-bounds access\nis undefined behavior",
        ]

        def _check():
            return VGroup(
                Line(ORIGIN, [0.18, 0.08, 0.0]),
                Line([0.18, 0.08, 0.0], [0.34, -0.13, 0.0]),
            ).set_stroke(cfg.COLOR_SAFE, width=6)

        def _triangle():
            return Triangle(color=cfg.COLOR_WARNING, fill_opacity=0.9).scale(0.28)

        def _lock():
            body = Rectangle(width=0.26, height=0.2, stroke_color=cfg.COLOR_WARNING,
                             stroke_width=3)
            shackle = Arc(
                radius=0.11, angle=3.14159, stroke_color=cfg.COLOR_WARNING,
                stroke_width=3,
            )
            shackle.move_to(body.get_top())
            return VGroup(body, shackle).scale(0.9)

        self.play(FadeIn(left_panel), FadeIn(left_title))
        self.wait(4)
        rows = []
        for i, statement in enumerate(left_statements):
            row = VGroup(_check(), _text(statement, font_size=18))
            row.arrange(RIGHT, buff=0.35)
            row.align_to(left_panel, LEFT).shift(RIGHT * 0.5 + DOWN * 0.05)
            row.shift(UP * (1.0 - i * 1.05 - row.get_center()[1]))
            rows.append(row)

        self.play(
            LaggedStart(
                *[
                    LaggedStart(FadeIn(row[0]), FadeIn(row[1], shift=UP * 0.15))
                    for row in rows
                ],
                lag_ratio=0.5,
                run_time=6,
            )
        )
        self.wait(8)

        self.play(FadeIn(right_panel), FadeIn(right_title))
        self.wait(4)
        right_rows = []
        for i, statement in enumerate(right_statements):
            marker = _triangle() if i == 0 else _lock()
            row = VGroup(marker, _text(statement, font_size=18))
            row.arrange(RIGHT, buff=0.35)
            row.align_to(right_panel, LEFT).shift(RIGHT * 0.5 + DOWN * 0.05)
            row.shift(UP * (1.0 - i * 1.05 - row.get_center()[1]))
            right_rows.append(row)

        self.play(
            FadeIn(right_rows[0][0]),
            FadeIn(right_rows[0][1], shift=UP * 0.15),
            run_time=1.5,
        )
        self.wait(6)
        # The undefined-behavior warning appears last, with a lock.
        self.play(
            FadeIn(right_rows[1][0]),
            FadeIn(right_rows[1][1], shift=UP * 0.15),
            run_time=1.5,
        )
        self.wait(15)
        _pad_to(self, SCENE_TARGETS["SafeModelClarificationScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# Scene 8: PhaseTransitionScene
# ---------------------------------------------------------------------------


class PhaseTransitionScene(Scene):
    """Project progression (Phase 1 -> 2 -> 3) and the film's takeaway:
    input length and buffer capacity are different quantities.

    Narration (docs/phase1_narration.md, Scene 8): "Phase 2 will show
    the real thing: an unchecked C-string copy with strcpy, where no
    cap exists — and what AddressSanitizer reports when the boundary is
    actually crossed. That belongs to the next phase. This phase ends
    where it began: with a clear picture of the boundary."
    """

    def construct(self):
        _mark_scene_start(self)
        header = _text("Project progression", font_size=32)
        header.to_edge(UP, buff=0.6)
        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(4.5)

        # Clear visual hierarchy: phase number badge (mono, phase color),
        # title (light), status tag (muted). No new technical claims.
        phases = [
            ("PHASE 1", "Visualize the boundary",
             "this film", cfg.COLOR_SAFE),
            ("PHASE 2", "Demonstrate the vulnerable strcpy operation",
             "next", cfg.COLOR_WARNING),
            ("PHASE 3", "Apply bounds-aware and layered defenses",
             "beyond", cfg.COLOR_BUFFER),
        ]
        for i, (number, title, status, color) in enumerate(phases):
            badge = _mono(number, font_size=26, color=color)
            title_text = _text(title, font_size=24)
            status_tag = _text(status, font_size=17, color=cfg.COLOR_OFFSET_LABEL)
            row = VGroup(badge, title_text, status_tag).arrange(RIGHT, buff=0.55)
            row.scale_to_fit_width(13.4)
            row.move_to([0.0, 1.3 - i * 1.2, 0.0])
            self.play(FadeIn(row, shift=UP * 0.2), run_time=2)
            self.wait(8)

        # The takeaway: input length and buffer capacity are different
        # quantities. Kept on screen long enough to read.
        rule = Line(
            LEFT * 4.5, RIGHT * 4.5, color=cfg.COLOR_CELL_STROKE, stroke_width=3
        )
        rule.move_to([0.0, -2.2, 0.0])
        takeaway = _text(
            "Input length != Buffer capacity",
            font_size=34,
            color=cfg.COLOR_INPUT,
        )
        takeaway.move_to([0.0, -2.9, 0.0])
        self.play(Create(rule), FadeIn(takeaway, shift=UP * 0.25), run_time=2.5)
        self.wait(22)
        _pad_to(self, SCENE_TARGETS["PhaseTransitionScene"])
        _scene_fade_out(self)


# ---------------------------------------------------------------------------
# The complete Phase 1 film: all eight scenes in order.
# One camera, one palette; every scene dissolves to black on exit so
# transitions are smooth and each demonstration starts cleanly (the
# program builds a fresh array for every input).
# ---------------------------------------------------------------------------

SCENE_CLASSES = [
    OpeningScene,
    ByteRepresentationScene,
    MemoryLayoutScene,
    SafeInputScene,
    BoundaryCrossingScene,
    HexDumpScene,
    SafeModelClarificationScene,
    PhaseTransitionScene,
]


class FullFilm(Scene):
    """All eight Phase 1 scenes, in film order (7:20 nominal)."""

    def construct(self):
        for scene_cls in SCENE_CLASSES:
            scene_cls.construct(self)
