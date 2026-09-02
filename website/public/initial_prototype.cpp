// Deep Dive Project - C++ Memory Management
// Topic: Stack vs Heap, Raw Pointers, Smart Pointers
// Week 2 - Initial Prototype

#include <iostream>
#include <memory> // For Smart Pointers
using namespace std;

// A simple struct to show memory layout
struct MyData {
  int id;
  char name[10];
};

int main() {
  cout << "=== C++ MEMORY MANAGEMENT DEMO ===" << endl;
  cout << "Stack vs Heap vs Smart Pointers" << endl;
  cout << "=================================" << endl << endl;

  // 1. STACK allocation (automatic - fast, limited size)
  MyData stackData;
  stackData.id = 42;
  cout << "[STACK] Address of stackData (struct): " << &stackData << endl;
  cout << "[STACK] Address of stackData.id:      " << &stackData.id << endl;
  cout << "[STACK] Size of struct:               " << sizeof(MyData) << " bytes"
       << endl;
  cout << endl;

  // 2. HEAP allocation (manual - raw pointer - DANGEROUS)
  MyData *heapData = new MyData();
  heapData->id = 100;
  cout << "[HEAP - RAW] Address of pointer variable: " << &heapData << endl;
  cout << "[HEAP - RAW] Address of actual object:    " << heapData << endl;
  cout << "[HEAP - RAW] Value of heapData->id:       " << heapData->id << endl;

  // !!! If I forget to delete, this causes a MEMORY LEAK !!!
  delete heapData; // I must remember to free the memory manually
  cout << endl;

  // 3. HEAP allocation (Smart Pointer – SAFE)
  unique_ptr<MyData> smartData = make_unique<MyData>();
  smartData->id = 200;
  cout << "[HEAP - SMART] Address of pointer variable: " << &smartData << endl;
  cout << "[HEAP - SMART] Address of actual object:    " << smartData.get()
       << endl;
  cout << "[HEAP - SMART] Value of smartData->id:      " << smartData->id
       << endl;
  cout << endl;

  // No delete needed! unique_ptr automatically frees memory when it goes out of
  // scope (RAII).

  cout << "=== SUMMARY ===" << endl;
  cout << "Stack:    Automatic allocation, fast, limited size." << endl;
  cout << "Heap:     Manual allocation (new/delete) – risk of memory leaks."
       << endl;
  cout << "Smart:    Automatic cleanup (RAII) – safe and modern C++." << endl;

  return 0;
}
