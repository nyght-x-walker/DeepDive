/*
 * C++ Memory Safety Deep Dive
 *
 * Phase 1:
 * Seeing the Boundary: Visualizing Logical Memory Regions
 *
 * This program uses one intentionally constructed contiguous
 * byte array to visualize how input bytes can cross a logical
 * buffer boundary.
 *
 * Important:
 * This is not an actual compiler-generated stack frame.
 * It does not claim that independent C++ variables are
 * guaranteed to appear next to one another in memory.
 *
 * The copy is limited to the total array size, so this phase
 * does not perform an actual out-of-bounds write.
 */

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <string>
#include <string_view>

constexpr std::size_t BUFFER_SIZE = 8;
constexpr std::size_t FLAG_SIZE = sizeof(std::uint32_t);
constexpr std::size_t SECOND_BUFFER_SIZE = 8;

constexpr std::size_t TOTAL_MEMORY_SIZE =
    BUFFER_SIZE + FLAG_SIZE + SECOND_BUFFER_SIZE;

void printSeparator() {
  std::cout << R"(

== == == == == == == == == == == == == == == == == == == == == == == == == == == == == == 
)";
}

void printHexByte(unsigned char byte) {
  std::cout << std::hex << std::setw(2) << std::setfill('0')
            << static_cast<unsigned int>(byte) << std::dec << std::setfill(' ');
}

void printMemory(const unsigned char *memory, std::size_t size) {
  std::cout << R"(
      Memory dump :

      Offset   Hexadecimal                         ASCII
      ------   ----------------------------------   ----------------
)";

  for (std::size_t i = 0; i < size; ++i) {
    std::cout << "  " << std::setw(2) << std::setfill('0') << i
              << std::setfill(' ') << "     ";
    printHexByte(memory[i]);
    std::cout << "                                ";
    if (memory[i] >= 32 && memory[i] <= 126) {
      std::cout << static_cast<char>(memory[i]);
    } else {
      std::cout << '.';
    }
    std::cout << '\n';
  }
}

void printPrintableRegion(const unsigned char *memory, std::size_t start,
                          std::size_t length) {
  for (std::size_t i = start; i < start + length; ++i) {
    if (memory[i] >= 32 && memory[i] <= 126) {
      std::cout << static_cast<char>(memory[i]);
    } else {
      std::cout << '.';
    }
  }
}

void demonstrateBoundary(std::string_view input) {
  printSeparator();

  std::cout << R"(INPUT: )" << input << R"(

Input size: )"
            << input.size() << R"( bytes

Logical buffer size: )"
            << BUFFER_SIZE << R"( bytes

)";

  /*
   * This array represents one contiguous educational
   * memory region.
   */
  std::array<unsigned char, TOTAL_MEMORY_SIZE> memory{};

  constexpr std::size_t bufferOffset = 0;
  constexpr std::size_t flagOffset = BUFFER_SIZE;
  constexpr std::size_t secondBufferOffset = BUFFER_SIZE + FLAG_SIZE;

  /*
   * Initialize the three logical regions.
   */

  const std::string initialBuffer = "SAFE";

  std::memcpy(memory.data() + bufferOffset, initialBuffer.data(),
              std::min(initialBuffer.size(), BUFFER_SIZE));

  const std::uint32_t criticalFlag = 0;

  std::memcpy(memory.data() + flagOffset, &criticalFlag, sizeof(criticalFlag));

  const std::string secondBuffer = "SECURE";

  std::memcpy(memory.data() + secondBufferOffset, secondBuffer.data(),
              std::min(secondBuffer.size(), SECOND_BUFFER_SIZE));

  std::cout << R"(
      Logical memory layout :

      +------------------------+
      |       buffer[8]        |
      +------------------------+
      |      criticalFlag      |
      +------------------------+
      |       buffer2[8]       |
      +------------------------+

      This is an intentionally constructed contiguous byte array.
      It is not an actual compiler-generated stack frame.

)";

  /*
   * Limit the copy to the total memory-model size.
   *
   * Therefore, this phase does not perform an actual
   * out-of-bounds write.
   */
  const std::size_t bytesToCopy = std::min(input.size(), memory.size());

  std::memcpy(memory.data(), input.data(), bytesToCopy);

  if (input.size() <= BUFFER_SIZE) {
    std::cout << R"(Result : input fits within the logical buffer.

)";
  } else {
    std::cout << R"(Result : input exceeds the logical buffer boundary.
Additional bytes enter adjacent logical regions
within this educational memory model.

)";
  }

  printMemory(memory.data(), memory.size());

  std::cout << R"(
      Region interpretation : 
      buffer[0..7]      : )";

  printPrintableRegion(memory.data(), bufferOffset, BUFFER_SIZE);

  std::cout << R"(
      criticalFlag bytes: )";

  for (std::size_t i = flagOffset; i < flagOffset + FLAG_SIZE; ++i) {
    printHexByte(memory[i]);
    std::cout << ' ';
  }

  std::cout << R"(
      buffer2 bytes     : )";

  printPrintableRegion(memory.data(), secondBufferOffset, SECOND_BUFFER_SIZE);

  std::cout << R"(

      Key lesson : A logical buffer boundary can be smaller than the
      contiguous memory region surrounding it.

)";
}

int main() {
  printSeparator();

  std::cout << R"(
PHASE 1:
SEEING THE BOUNDARY
VISUALIZING LOGICAL MEMORY REGIONS

This program demonstrates how input bytes may cross
from one logical region into adjacent regions.

The model contains :
  - buffer[8]
  - criticalFlag
  - buffer2[8]

)";

  demonstrateBoundary("HELLO");
  demonstrateBoundary("ABCDEFGHIJKLMNO");

  printSeparator();

  std::cout << R"(
END OF PHASE 1

Important distinction : This phase visualizes a boundary safely.
The next phase demonstrates an actual vulnerable
operation using an unchecked C-string copy.

)";

  return 0;
}
