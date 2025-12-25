# Virtual-Block-Storage-Device

## Overview

This repository contains a Python simulation of a **block storage device** and its corresponding **device driver layer**.
The project models how an operating system interacts with storage hardware at a low level, including block-based I/O, driver validation, error handling, and logging.

No real hardware is accessed — all behavior is simulated using Python standard libraries.

---

## Objectives

The project is designed to demonstrate:

* Understanding of block-based storage concepts
* Device vs. driver separation
* Low-level I/O request handling
* Robust error handling and retries
* Clean system-oriented code structure
* Logging and monitoring practices

---

## System Architecture

The implementation is split into **two layers**, mirroring real operating system design:

### 1. Virtual Device Layer

* Simulates raw storage hardware
* Operates strictly on fixed-size blocks
* Has no knowledge of offsets or partial reads/writes

### 2. Device Driver Layer

* Acts as an intermediary between users and the device
* Translates byte offsets into block operations
* Enforces validation rules and block state constraints
* Handles retries and raises meaningful exceptions

---

## Storage Model

| Property     | Value              |
| ------------ | ------------------ |
| Total Size   | 8 MB               |
| Block Size   | 4096 bytes         |
| Total Blocks | 2048               |
| Backend      | Python `bytearray` |

The storage backend is a contiguous `bytearray`, simulating disk memory.

---

## Block States

Each block has an associated state:

* **FREE** – Block has never been written
* **USED** – Block contains valid data
* **TRIMMED** – Block marked as unused
* **BAD** – Block is permanently unusable

Block state management is critical to enforcing correct read/write behavior.

---

## Virtual Device Interface

Implemented in `device.py`:

```python
read_block(block_id) -> bytes
write_block(block_id, data: bytes)
trim_block(block_id)
get_stats() -> dict
```

All operations work on **exactly one block**.

---

## Device Driver Interface

Implemented in `driver.py`:

```python
read(offset: int, size: int) -> bytes
write(offset: int, data: bytes)
trim(offset: int, size: int)
```

The driver:

* Validates all requests
* Converts offsets to block IDs
* Handles partial blocks
* Enforces block state rules
* Retries failed writes (up to 3 attempts)

---

## TRIM Behavior

* `trim()` marks blocks as `TRIMMED`
* Reading trimmed blocks returns **zero-filled data**
* Trimmed blocks may be reused by future writes
* TRIM does not physically erase memory

This simulates SSD discard behavior.

---

## Error Handling

Custom exception classes are used to clearly represent failure conditions, including:

* Out-of-bounds access
* Invalid block operations
* BAD block access
* Partial writes
* Retry exhaustion
* Simulated device failures

Errors are surfaced at the driver level with meaningful messages.

---

## Logging & Monitoring

The system logs:

* All read, write, and trim operations
* Retry attempts
* Errors and failures
* Device statistics

Example statistics:

* Total reads
* Total writes
* Trim operations
* Failed operations

---

## Testing

The implementation includes tests that verify:

* Write → Read data integrity
* Trim → Read returns zero-filled data
* Out-of-bounds access raises exceptions
* BAD block access is rejected
* Sequential read/write correctness

All tests must pass for a valid implementation.

---

## Project Structure

```
device_driver/
├── device.py       # Virtual block storage device
├── driver.py       # Device driver logic
├── constants.py    # Shared constants
├── exceptions.py   # Custom exception classes
├── tests.py        # Unit tests
└── README.md       # Documentation
```

---

## Constraints

* Python standard library only
* No real hardware access
* Emphasis on clean, readable, maintainable code

---

## Learning Outcomes

This project demonstrates practical understanding of:

* Low-level storage systems
* Block-based I/O
* OS-style driver abstractions
* Defensive programming
* Error recovery strategies
* System observability through logging

---

## Summary

This repository provides a realistic simulation of how an operating system communicates with a block storage device through a device driver.
It emphasizes correctness, robustness, and clear system design over raw performance.

---
