"""Shared constants for the Phase 1 boundary animation.

All numeric values are derived from and verified against
``src/phase1_boundary_model.cpp`` and ``outputs/phase1_output.txt``.
This module must stay free of Manim imports so it can be unit-tested.
"""

# ---------------------------------------------------------------------------
# Memory model sizes (verified: src/phase1_boundary_model.cpp:30-35)
# ---------------------------------------------------------------------------

BUFFER_SIZE = 8
FLAG_SIZE = 4
SECOND_BUFFER_SIZE = 8
TOTAL_MEMORY_SIZE = BUFFER_SIZE + FLAG_SIZE + SECOND_BUFFER_SIZE

# Region offsets (verified: src/phase1_boundary_model.cpp:101-103)
BUFFER_OFFSET = 0
FLAG_OFFSET = BUFFER_SIZE
SECOND_BUFFER_OFFSET = BUFFER_SIZE + FLAG_SIZE

# ---------------------------------------------------------------------------
# Test inputs (verified: outputs/phase1_output.txt)
# ---------------------------------------------------------------------------

SAFE_INPUT = "HELLO"
OVERSIZED_INPUT = "ABCDEFGHIJKLMNO"

# Input text -> expected byte length (program-verified).
EXPECTED_INPUT_LENGTHS = {
    SAFE_INPUT: 5,
    OVERSIZED_INPUT: 15,
}

# Initial region contents (verified: src/phase1_boundary_model.cpp:109-121)
INITIAL_BUFFER = "SAFE"
INITIAL_FLAG_BYTES = [0x00] * FLAG_SIZE
INITIAL_SECOND_BUFFER = "SECURE"

# ---------------------------------------------------------------------------
# Color palette (dark background, high contrast; labels always accompany
# color so no information is carried by color alone).
# ---------------------------------------------------------------------------

COLOR_BACKGROUND = "#0e1116"
COLOR_BUFFER = "#4d9de0"       # blue: logical buffer
COLOR_FLAG = "#e8930c"         # orange: critical flag
COLOR_SECOND_BUFFER = "#3fa34d"  # green: second buffer
COLOR_INPUT = "#f2c14e"        # yellow: input bytes
COLOR_WARNING = "#e0473a"      # red: boundary violation
COLOR_SAFE = "#66bb6a"         # green: safe / fits status
COLOR_TEXT = "#f5f6f7"         # light text on dark background

# Neutral surface colors for cells, separators, and offset labels.
COLOR_CELL_FILL = "#141a23"
COLOR_CELL_STROKE = "#2b3644"
COLOR_OFFSET_LABEL = "#8a97a8"

FONT_MONO = "DejaVu Sans Mono"
FONT_SANS = "DejaVu Sans"