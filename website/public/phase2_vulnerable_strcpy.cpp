/*
 * C++ Memory Safety Deep Dive Phase 2
 * Demonstrating the Vulnerable strcpy Operation
 *
 * EDUCATIONAL DEMONSTRATION ONLY INTENTIONALLY VULNERABLE
 *
 * This program intentionally performs an unchecked strcpy into a
 * fixed size buffer to demonstrate why the operation is unsafe and
 * how AddressSanitizer detects the resulting out of bounds write.
 *
 * SAFETY DISCLAIMER:
 *   Do not use this pattern in production code.
 *   strcpy does not receive the destination capacity. If the
 *   source is longer than the destination, the write past the end
 *   is undefined behavior.
 *   Run only locally in an isolated development environment
 *   preferably with fsanitize=address,undefined.
 *   No exploit payload, no return address overwrite, no ROP chain,
 *   no external target, no real credentials are involved.
 *
 * Relationship to Phase 1:
 *   Phase 1 used one array unsigned char 20 and capped every copy with
 *   std::min, no real out of bounds write, only a visualization. Phase 2
 *   removes the cap and performs a real unchecked copy so the same 8 byte
 *   boundary is actually crossed.
 *
 * Expected sizes verified against outputs/phase1_output.txt:
 *   BUFFER_SIZE equals 8
 *   Oversized input ABCDEFGHIJKLMNO equals 15 bytes, excess 7
 *   Safe input 1234567 equals 7 bytes, fits 7 plus null fits exactly
 */

#include <cstring>
#include <iostream>

constexpr std::size_t BUFFER_SIZE = 8;

// Isolated vulnerable function, contains the only unsafe operation
// in this file. Kept minimal so the AddressSanitizer report points
// clearly at the strcpy line.
void vulnerableFunction(const char *input) {
  char buffer[BUFFER_SIZE];

  std::cout << "\n[VULNERABLE FUNCTION]\n";
  std::cout << "Buffer capacity: " << BUFFER_SIZE << " bytes\n";
  std::cout << "Input: \"" << input << "\"\n";
  std::cout << "Input length: " << std::strlen(input) << " bytes\n";
  std::cout << "Calling strcpy(buffer, input)...\n";

  // SECURITY BUG strcpy does not know BUFFER_SIZE
  // If strlen input is greater or equal to BUFFER_SIZE, the terminating null also
  // overflows. The write beyond buffer is undefined behavior.
  // AddressSanitizer will report stack buffer overflow WRITE of size 16 at [32,40) buffer
  std::strcpy(buffer, input);

  // If execution reaches here for the oversized input, the program
  // has already performed an invalid memory access.
  std::cout << "Buffer contains: \"" << buffer << "\"\n";
}

int main() {
  std::cout << "============================================================\n";
  std::cout << "  PHASE 2 DEMONSTRATING THE VULNERABLE strcpy OPERATION\n";
  std::cout << "  Educational demonstration only intentionally vulnerable\n";
  std::cout << "============================================================\n";
  std::cout << "\nThis program is isolated and local. No external target,\n";
  std::cout << "no exploit payload, no real credentials are used.\n";
  std::cout << "Run with AddressSanitizer to see the diagnostic.\n";

  std::cout << "\nControl: safe input 7 bytes fits \n";
  vulnerableFunction("1234567");

  std::cout << "\nTest: oversized input 15 bytes exceeds 8 \n";
  std::cout << "Expect AddressSanitizer stack buffer overflow\n";
  vulnerableFunction("ABCDEFGHIJKLMNO");

  std::cout << "\n============================================================\n";
  std::cout << "  END OF PHASE 2 DEMO if reached, out of bounds already occurred\n";
  std::cout << "============================================================\n";
  return 0;
}
