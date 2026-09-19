/*
 * C++ Memory Safety Deep Dive Phase 3
 * Defended copy with explicit bounds
 *
 * Safe demonstration. No vulnerability in this file.
 * It shows the fix for the Phase 2 strcpy overflow.
 * Phase 2 code was intentionally vulnerable.
 * That vulnerable code must run only locally with sanitizer.
 */
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <string_view>

constexpr std::size_t BUFFER_SIZE = 8;

// Fixed copy with explicit bound
// Keeps room for null terminator
void fixedFunction(std::string_view input) {
  std::array<char, BUFFER_SIZE> buffer{};
  std::cout << "\n[FIXED FUNCTION]\n";
  std::cout << "Buffer capacity: " << BUFFER_SIZE << " bytes\n";
  std::cout << "Input: \"" << input << "\"\n";
  std::cout << "Input length: " << input.size() << " bytes\n";
  // Copy at most 7 plus null
  const std::size_t n = std::min(input.size(), BUFFER_SIZE - 1);
  std::memcpy(buffer.data(), input.data(), n);
  buffer[n] = '\0';
  std::cout << "Bytes copied: " << n << "\n";
  if (input.size() >= BUFFER_SIZE) {
    std::cout << "Input truncated safely.\n";
  } else {
    std::cout << "Input fit exactly.\n";
  }
  std::cout << "Buffer contains: \"" << buffer.data() << "\"\n";
  std::cout << "Status: TRUNCATED SAFELY or FITS, no overflow.\n";
}

int main() {
  std::cout << "============================================================\n";
  std::cout << "  PHASE 3 DEFENDED COPY OPERATION\n";
  std::cout << "  Safe demonstration, bounds enforced\n";
  std::cout << "============================================================\n";
  std::cout << "\nSame numbers as Phase 1 and Phase 2.\n";
  std::cout << "Buffer 8. Oversized input 15. Write 16 blocked.\n";
  std::cout << "\nControl: safe input 7 bytes fits\n";
  fixedFunction("1234567");
  std::cout << "\nTest: oversized input 15 bytes blocked\n";
  std::cout << "Expect truncation, exit 0, no sanitizer report\n";
  fixedFunction("ABCDEFGHIJKLMNO");
  std::cout << "\n============================================================\n";
  std::cout << "  END OF PHASE 3 DEMO, boundary enforced\n";
  std::cout << "============================================================\n";
  return 0;
}
