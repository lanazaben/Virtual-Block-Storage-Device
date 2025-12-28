import random

from constants import (
    DEVICE_SIZE_BYTES,
    BLOCK_SIZE_BYTES,
    TOTAL_BLOCKS,
    BLOCK_FREE,
    BLOCK_USED,
    BLOCK_TRIMMED,
    BLOCK_BAD,
    STAT_READS,
    STAT_WRITES,
    STAT_TRIMS,
    STAT_FAILURES,
)

from exceptions import (
    InvalidBlockError,
    BadBlockError,
    TrimmedBlockReadError,
    DeviceIOError,
)


class VirtualBlockDevice:
    """
    Virtual Block Storage Device.
    Simulates low-level block-based storage behavior.
    """

    def __init__(self, simulate_failure=True):
        self.simulate_failure = simulate_failure
        self.total_blocks = TOTAL_BLOCKS

        # Raw storage memory (simulates disk sectors)
        self._storage = bytearray(DEVICE_SIZE_BYTES)

        # Track the state of each block independently
        self._block_states = [BLOCK_FREE] * TOTAL_BLOCKS

        # Device-level statistics for monitoring and debugging
        self._stats = {
            STAT_READS: 0,
            STAT_WRITES: 0,
            STAT_TRIMS: 0,
            STAT_FAILURES: 0,
        }

    # =========================
    # Internal Helpers
    # =========================

    def _validate_block_id(self, block_id: int):
        if not isinstance(block_id, int):
            raise InvalidBlockError("Block ID must be an integer")

        if block_id < 0 or block_id >= TOTAL_BLOCKS:
            raise InvalidBlockError(f"Invalid block ID: {block_id}")

    def _simulate_io_failure(self):
        """
        Simulate random hardware I/O failures.
        Disabled during testing.
        """
        if self.simulate_failure and random.random() < 0.05:
            self._stats[STAT_FAILURES] += 1
            raise DeviceIOError("Simulated device I/O failure")

    # =========================
    # Public Device Interface
    # =========================

    def read_block(self, block_id: int) -> bytes:
        self._validate_block_id(block_id)

        state = self._block_states[block_id]

        # BAD blocks are permanently unusable
        if state == BLOCK_BAD:
            self._stats[STAT_FAILURES] += 1
            raise BadBlockError(f"Cannot read BAD block {block_id}")

        # TRIMMED blocks are logically empty
        if state == BLOCK_TRIMMED:
            return b"\x00" * BLOCK_SIZE_BYTES

        # Simulate random hardware failure
        self._simulate_io_failure()

        start = block_id * BLOCK_SIZE_BYTES
        end = start + BLOCK_SIZE_BYTES

        self._stats[STAT_READS] += 1
        return bytes(self._storage[start:end])

    def write_block(self, block_id: int, data: bytes):
        self._validate_block_id(block_id)

        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")

        if len(data) != BLOCK_SIZE_BYTES:
            raise ValueError(
                f"Write size must be exactly {BLOCK_SIZE_BYTES} bytes"
            )

        state = self._block_states[block_id]

        # Writing to BAD blocks is forbidden
        if state == BLOCK_BAD:
            self._stats[STAT_FAILURES] += 1
            raise BadBlockError(f"Cannot write to BAD block {block_id}")

        # Simulate random hardware failure
        self._simulate_io_failure()

        start = block_id * BLOCK_SIZE_BYTES
        end = start + BLOCK_SIZE_BYTES

        self._storage[start:end] = data
        self._block_states[block_id] = BLOCK_USED
        self._stats[STAT_WRITES] += 1

    def trim_block(self, block_id: int):
        self._validate_block_id(block_id)

        if self._block_states[block_id] == BLOCK_BAD:
            self._stats[STAT_FAILURES] += 1
            raise BadBlockError(f"Cannot trim BAD block {block_id}")

        self._block_states[block_id] = BLOCK_TRIMMED
        self._stats[STAT_TRIMS] += 1

    def get_stats(self) -> dict:
        return dict(self._stats)

    # =========================
    # Testing / Maintenance Hook
    # =========================

    def mark_block_bad(self, block_id: int):
        """
        Explicitly mark a block as BAD.
        Used for testing and fault injection.
        """
        self._validate_block_id(block_id)
        self._block_states[block_id] = BLOCK_BAD

