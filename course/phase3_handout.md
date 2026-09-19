# Phase 3 Handout

## My defended copy operation

This handout is about my fix. It matters because I use the same 8 byte buffer and the same 15 byte input as Phase 2, but my program stays defined. I prove that a bound before copy plus layers behind it hold my line.

After this handout you will know. How I copy with explicit bounds. Why my truncation is safe. How my clean test differs from my crash test. Which layers back up my code. How to reproduce my builds.

## Key terms

Stack. Short lived memory for calls. Analogy. Tray in active treatment.

Heap. Long lived memory for dynamic objects. Analogy. Labeled shelves for later treatment.

Buffer. My fixed 8 byte region. Analogy. Egg carton with 8 spots.

Memory. Bytes at addresses that my program can read or write.

Pointer. Address of a byte. Analogy. Slip with a house number.

Smart pointer. Pointer that frees its memory on its own. Analogy. Self returning library book.

strcpy. C copy that runs until null. It takes no destination size. Analogy. Pouring without counting cup size.

AddressSanitizer. Test tool with sanitizer flag. It reports bad writes. It does not fix.

Core lesson. Input length is not buffer capacity. I check each time.

## How parts connect

My pointer selects my buffer in stack memory. My fixed copy checks my capacity of 8. My sanitizer confirms no bad write at offset 40. My layers guard what code misses. My film shows each step in order.

Numbers I keep. Buffer 8. Input 15. Blocked write 16. Offset 40 guarded. Hex 41 to 4F.

## My fixed code

File src/phase3_fixed_copy.cpp, safe demo, 60 lines style, isolated.

I set BUFFER_SIZE 8. I compute n as min of input size and 7. I copy n with memcpy. I set null at n. I print copied count plus truncation flag.

Safe input 1234567 gives n 7, fits, result 1234567. Oversized ABCDEFGHIJKLMNO gives n 7, truncated safely, result ABCDEFG. Blocked 8. Hex kept 41 to 47. Hex 48 to 4F blocked. Exit 0.

Safety note. My Phase 2 code was intentionally vulnerable. That code must run only locally with sanitizer. My Phase 3 code here is safe.

## My clean proof

Plain build exits 0 with truncation message. Sanitizer build with address plus undefined flags exits 0 with no ERROR and no stack buffer overflow. No ABORTING.

Contrast. Phase 2 same input gives ERROR stack buffer overflow, WRITE size 16, buffer 32 to 40, offset 40, ABORTING, exit 1. Raw Phase 2 without sanitizer gives stack smashing, exit 134, or silent pass. Both are allowed undefined behavior. My Phase 3 stays exit 0 in all builds.

## My layers

Size aware code prevents my bad write. Sanitizer finds issues in tests. Canary aborts my corrupt path. ASLR hides addresses. NX slash DEP blocks run from data. Flow check limits jumps. Static scan flags risky calls early. No single layer is sufficient.

## Reproduce my builds

Run in my project folder on a local machine.

Plain. g++ -std=c++20 -Wall -Wextra -Wpedantic -g src/phase3_fixed_copy.cpp -o phase3_fixed, then run phase3_fixed.

Sanitizer. g++ -std=c++20 -Wall -Wextra -Wpedantic -fsanitize=address,undefined -g src/phase3_fixed_copy.cpp -o phase3_fixed_asan, then run phase3_fixed_asan.

Tests. uv run python -m pytest tests/test_phase3_data.py -v

Deck. Open website/src/pages/slides/phase3 on my site. Press Start. Follow notes.

Film. No video render ships. I present live from my slides.

## Files

Source, outputs, deck, audio, video, narration, captions, this handout, explanation, spec, site pages. My styled handout page lives on my site. My raw docs stay as source.
