# Virtual-Block-Storage-Device
1. Project Overview
This project simulates a block storage device and its corresponding device driver layer using Python.
The goal is to demonstrate understanding of low-level system design concepts such as block-based I/O, device drivers, error handling, and storage state management — without interacting with real hardware.
The implementation mirrors how an operating system communicates with storage hardware through a driver abstraction.
2. Design Philosophy
The system is intentionally split into two layers:
Virtual Device Layer
Simulates raw storage hardware that operates strictly on fixed-size blocks.
Device Driver Layer
Acts as a controller between user-level requests (byte offsets and sizes) and the low-level device operations.
This separation reflects real-world OS architecture and enforces clean responsibility boundaries.
3. Storage Model
3.1 Device Characteristics
Property	Value
Total Size	8 MB
Block Size	4096 bytes (4 KB)
Total Blocks	2048
Backend	Python bytearray
The entire storage space is represented as a contiguous byte array:
bytearray(8 * 1024 * 1024)
3.2 Block States
Each block maintains a state to simulate real storage behavior:
State	Description
FREE	Block has never been written
USED	Block contains valid data
TRIMMED	Block marked as unused
BAD	Block is permanently unusable
Block states are tracked independently from the storage data.
4. Virtual Device Layer (device.py)
The virtual device simulates raw hardware and only understands block-based operations.
4.1 Responsibilities
Read and write individual blocks
Track block states
Handle TRIM operations
Collect device statistics
Simulate hardware failures
The device does not understand offsets, files, or partial reads.
4.2 Device Interface
read_block(block_id) -> bytes
write_block(block_id, data: bytes)
trim_block(block_id)
get_stats() -> dict
Each method operates on exactly one block.
5. TRIM Behavior
TRIM simulates SSD discard functionality:
trim_block() marks a block as TRIMMED
Reading a trimmed block returns zero-filled data
Trimmed blocks may be reused by future writes
TRIM does not physically erase memory
This behavior enforces correct state handling and reuse logic.
6. Device Driver Layer (driver.py)
The device driver translates user-level requests into block operations.
6.1 Driver Responsibilities
Validate all read/write requests
Translate byte offsets to block IDs
Handle partial block reads and writes
Enforce block state rules
Retry failed writes (up to 3 attempts)
Raise meaningful exceptions
Log all operations and failures
6.2 Driver Interface
read(offset: int, size: int) -> bytes
write(offset: int, data: bytes)
trim(offset: int, size: int)
Users interact only with the driver, never directly with the device.
7. Offset-to-Block Translation
The driver converts byte offsets into block operations using:
block_id = offset // BLOCK_SIZE
block_offset = offset % BLOCK_SIZE
This allows the driver to correctly handle:
Partial block writes
Multi-block reads
Boundary conditions
8. Error Handling Strategy
The system uses custom exception classes to ensure clear and precise failure reporting.
Examples:
Out-of-bounds access
Invalid block access
BAD block usage
Retry exhaustion
Simulated I/O failures
This mirrors real operating system error models.
9. Logging & Monitoring
The system logs:
All read/write/trim operations
Retry attempts
Errors and failures
Device statistics
Statistics include:
Total reads
Total writes
Trim operations
Failed operations
This enables observability similar to real system diagnostics.
10. Testing
The implementation is validated using mandatory test scenarios:
✔ Write data → Read data → Data matches
✔ Trim data → Read → Zero-filled result
✔ Write beyond device size → Exception
✔ Access BAD block → Exception
✔ Multiple sequential reads and writes
All tests ensure correctness, robustness, and state consistency.
11. Project Structure
device_driver/
├── device.py       # Virtual storage device
├── driver.py       # Device driver layer
├── constants.py    # Shared constants
├── exceptions.py   # Custom exceptions
├── tests.py        # Unit tests
└── README.md       # Project documentation
12. Constraints & Tools
Python standard library only
No real hardware access
Clean, readable, and maintainable code
Modular and testable design
13. Learning Outcomes
This project demonstrates:
Low-level system design thinking
Layered architecture
Block-based I/O concepts
Robust error handling
Defensive programming
Logging and observability
Real-world OS driver principles
14. Summary
This project simulates how an operating system interacts with a block storage device through a device driver.
By abstracting hardware behavior and enforcing strict state and error rules, the system provides a realistic and educational model of storage I/O — implemented entirely in Python.
