# Phase 1 Handout

## Seeing the Boundary: Visualizing Logical Memory Regions in C++

C++ Memory Safety Deep Dive, Phase 1
Interactive site: https://nyght-x-walker.github.io/DeepDive/
Film online: https://nyght-x-walker.github.io/DeepDive/videos/phase1.mp4

## Abstract

C++ gives the programmer direct control over memory. That control creates a boundary between input length and buffer capacity. This phase builds a deterministic, contiguous 20 byte memory model to show two cases. First, an input that fits inside a logical buffer. Second, an input that crosses the boundary into adjacent logical regions. The demonstration is safe. The program caps every copy at the model total size, so no out of bounds write occurs. A real out of bounds access in C++ is undefined behavior. Phase 2 shows a real vulnerable case.

Film length: 9 minutes 41 seconds, 581 seconds total. Each scene audio starts 0.5 seconds after scene start. Captions are timed to speech windows.

## How to Use This Handout

* Watch the animation once without pausing to follow the story.
* Rewatch Scene 3 for the memory layout: three logical regions and boundaries inside one contiguous array.
* Rewatch Scene 5 for the boundary crossing: where the fifteen input bytes land and why the crossing is visualized, not performed.
* Use Scene 6 and the dump table to connect offsets, hex, and ASCII, reading the same memory the way the program prints it.
* Use Scene 7 to distinguish the safe model from real undefined behavior.

## Key Concepts

* **Byte**: 8 bits. Smallest addressable unit. One byte can be written in binary, hexadecimal, or ASCII.
* **Buffer**: Named region that stores a fixed number of bytes. Here, `buffer[8]` is the logical buffer under test.
* **Capacity**: Number of bytes a buffer can hold. Fixed at creation. `buffer[8]` capacity is 8 bytes.
* **Offset**: Position of a byte inside the model, starting at 00. Model covers 00 to 19.
* **Hexadecimal**: Base 16 notation. One byte equals two hex digits. `0x41` equals 65, ASCII code for `A`.
* **ASCII**: Standard mapping from byte values to symbols. `0x41` is `A`, `0x4a` is `J`, `0x4f` is `O`.
* **Logical boundary**: End of the logical buffer at offset 07. Bytes at 08 and beyond belong to adjacent regions.
* **Contiguous memory**: Bytes stored in adjacent cells of one array at consecutive offsets 00 to 19.
* **Undefined behavior (UB)**: What a real out of bounds access is in C++. The standard imposes no requirements.
* **Input length**: Bytes the input contains. `HELLO` is 5, `ABCDEFGHIJKLMNO` is 15.
* **Logical region**: Named slice with a purpose. `buffer[8]`, `criticalFlag`, `buffer2[8]`.
* **Boundary crossing**: Input bytes appearing beyond the logical boundary.
* **std::min**: Helper used by Phase 1. `std::min(input.size(), memory.size())` keeps every copy inside the 20 byte model.
* **strcpy**: Unchecked C-string copy. Receives no destination capacity. Previewed in Phase 2.
* **AddressSanitizer**: Runtime detector (`-fsanitize=address`) that reports out of bounds accesses. Used in Phase 2.

Core lesson: input length and buffer capacity are separate quantities. Length is how many bytes the input has. Capacity is how many bytes the buffer can hold.

## The Memory Model

One contiguous array of 20 bytes, divided into three logical regions. This is a constructed educational model. It is not a compiler generated stack frame. It does not claim independent variables sit adjacently in real memory.

![Memory layout of the 20-byte model](phase1_layout.svg)

```
offset:  00 01 02 03 04 05 06 07 | 08 09 10 11 | 12 13 14 15 16 17 18 19
region:        buffer[8]         | criticalFlag|         buffer2[8]
```

* `buffer[8]`: logical buffer under test (blue).
* `criticalFlag`: 4 bytes, `sizeof(std::uint32_t)` on this system (orange).
* `buffer2[8]`: second logical region (green).
* Red dashed line marks the logical boundary at the end of `buffer[8]` at offset 07.

Initial contents as the program sets them: `SAFE` in the buffer at 00 to 03, four zero bytes in the flag at 08 to 11, `SECURE` in the second buffer at 12 to 17. Offsets 04 to 07 and 18 to 19 start as zero so unused capacity is visible.

## Demonstration 1: Input That Fits, HELLO

* Input size: 5 bytes
* Logical buffer size: 8 bytes
* Status: FITS

`H E L L O` occupy 00 to 04. Offsets 05 to 07 stay zero. Flag and second buffer are unchanged. Flag bytes are `00 00 00 00`. Second buffer is `SECURE` with two trailing zeroes. Check: 5 is less than or equal to 8, so capacity holds the input.

## Demonstration 2: Input That Crosses, ABCDEFGHIJKLMNO

* Input size: 15 bytes
* Logical buffer size: 8 bytes
* Excess: 7 bytes
* Status: BOUNDARY CROSSED

* A to H fill 00 to 07. Logical buffer is full.
* I, J, K, L (`0x49 0x4a 0x4b 0x4c`) appear at 08 to 11, the flag cells.
* M, N, O appear at 12 to 14, start of the second buffer, leaving `URE` at 15 to 17.

In this constructed model, the remaining bytes appear in adjacent logical regions. The program prints this exact result in its dump.

## The Dump, offsets 00 to 14

```
Offset   Hex   ASCII
00       41    A
01       42    B
02       43    C
03       44    D
04       45    E
05       46    F
06       47    G
07       48    H
08       49    I
09       4a    J
10       4b    K
11       4c    L
12       4d    M
13       4e    N
14       4f    O
```

Hex letters are lowercase as the C++ program prints with `std::hex`. Values are standard ASCII codes `0x41` to `0x4f`.

## The Key Lesson

Input length and buffer capacity are different quantities. When an input exceeds the logical buffer boundary, the additional bytes may overwrite adjacent data in an unsafe real world implementation.

## Safe Visualization vs Real Vulnerability

* **Phase 1, this phase**:
  * Mechanism: one `std::array` of 20 bytes, copy capped with `std::min`.
  * Out of bounds write: none. Every byte stays inside the 20 byte model.
  * Behavior: deterministic, safe to run.
  * Purpose: teach the boundary visually.

* **Phase 2, preview**:
  * Mechanism: unchecked `strcpy` into a fixed buffer.
  * Out of bounds write: real, actual.
  * Behavior: undefined behavior, detected by AddressSanitizer.
  * Purpose: show the real consequence.

Phase 1 does not perform an actual out of bounds write. It never overwrites a return address and contains no exploit. Every copy is capped at the model total size by `std::min`, so all bytes stay inside the 20 byte array. The crossing is a visualization of where bytes would land in an unsafe implementation. A real out of bounds access in C++ is undefined behavior. Phase 2 shows it with `strcpy` under AddressSanitizer.

## Next Phase Preview

Phase 2, Demonstrate the vulnerable strcpy operation, moves from the safe model to a real vulnerable operation:

* Unchecked C-string copy with `strcpy` into a fixed size buffer. No `std::min` cap, no bounds check.
* Genuine out of bounds write. Bytes are written past the buffer end into adjacent memory, as in a classic buffer overflow.
* Compilation with AddressSanitizer (`-fsanitize=address`) and review of its diagnostic report. The exact out of bounds access is reported at runtime.
* Direct comparison. Logical boundary lesson from this film played out as a real undefined behavior event.

Phase 1 contains only the safe visualization. Phase 2 executes the real vulnerability under sanitizer supervision. Phase 3, Apply bounds aware and layered defenses, shows how bounds checks, safer interfaces, and layered mitigations prevent it.

## Verification, how these numbers were confirmed

The program was compiled on the target system and run to produce `outputs/phase1_output.txt`:

```
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wformat=2 -g \
    src/phase1_boundary_model.cpp -o phase1_boundary_model
./phase1_boundary_model > outputs/phase1_output.txt
```

The animation renders the same model. Tests: `uv run python -m pytest tests -q`:

```
PYTHONPATH=. uv run manim render -ql animation/phase1_boundary_animation.py FullFilm
```

Confirmed: `HELLO` is 5 bytes, `ABCDEFGHIJKLMNO` is 15 bytes, `BUFFER_SIZE` is 8, `FLAG_SIZE` is `sizeof(std::uint32_t)` is 4, `SECOND_BUFFER_SIZE` is 8, `TOTAL_MEMORY_SIZE` is 20, offsets 00 to 19, copy limited by `std::min(input.size(), memory.size())`, exit code 0.

## Files

* `src/phase1_boundary_model.cpp`: authoritative C++ program.
* `outputs/phase1_output.txt`: verified program output.
* `docs/phase1_narration.md`: scene by scene narration and transcript.
* `docs/phase1_captions.srt`: 54 caption cues, timed to spoken audio within each scene (scene boundaries 0, 42, 107, 183, 243, 343, 427, 515 seconds).
* `docs/phase1_layout.svg`: memory layout diagram shown above.
* `animation/`: Manim source (config, components, scenes).
* `tests/test_animation_data.py`: tests for the data model.

## Suggested Reading

* C++ standard, [basic], [dcl.array], [expr.add]: arrays and pointer arithmetic. Out of bounds access is undefined behavior.
* AddressSanitizer documentation for the Phase 2 demonstration.
