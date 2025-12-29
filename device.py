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

    def __init__(self, simulate_failure=True):
        self.simulate_failure = simulate_failure

        # Raw storage
        self._storage = bytearray(DEVICE_SIZE_BYTES)
        self.total_size_bytes = DEVICE_SIZE_BYTES

        # Physical block states
        self._block_states = [BLOCK_FREE] * TOTAL_BLOCKS

        # LBA <-> Physical block mappings
        self._lba_to_pba = {}
        self._pba_to_lba = {}

        # Free physical blocks
        self._free_blocks = set(range(TOTAL_BLOCKS))

        # Statistics
        self._stats = {
            STAT_READS: 0,
            STAT_WRITES: 0,
            STAT_TRIMS: 0,
            STAT_FAILURES: 0,
        }


    def _validate_block_id(self, block_id: int):
        if not isinstance(block_id, int):
            raise InvalidBlockError("Block ID must be an integer")
        if block_id < 0 or block_id >= TOTAL_BLOCKS:
            raise InvalidBlockError(f"Invalid block ID: {block_id}")

    def _simulate_io_failure(self):
        if self.simulate_failure and random.random() < 0.05:
            self._stats[STAT_FAILURES] += 1
            raise DeviceIOError("Simulated device I/O failure")

    def _allocate_block(self) -> int:
        if not self._free_blocks:
            reclaimed = self.garbage_collect()
            if reclaimed == 0:
                raise DeviceIOError("Storage full: no reclaimable blocks")

        return self._free_blocks.pop()

    # Garbage Collection
    def garbage_collect(self) -> int:
        reclaimed = 0

        for pba in list(self._pba_to_lba.keys()):
            if self._block_states[pba] == BLOCK_TRIMMED:
                lba = self._pba_to_lba.pop(pba)
                self._lba_to_pba.pop(lba, None)

                self._block_states[pba] = BLOCK_FREE
                self._free_blocks.add(pba)
                reclaimed += 1

        return reclaimed

    def read_block_lba(self, lba: int) -> bytes:
        if lba not in self._lba_to_pba:
            return b"\x00" * BLOCK_SIZE_BYTES

        pba = self._lba_to_pba[lba]
        state = self._block_states[pba]

        if state == BLOCK_BAD:
            self._stats[STAT_FAILURES] += 1
            raise BadBlockError(f"Cannot read BAD block {pba}")

        if state == BLOCK_TRIMMED:
            return b"\x00" * BLOCK_SIZE_BYTES

        self._simulate_io_failure()

        start = pba * BLOCK_SIZE_BYTES
        end = start + BLOCK_SIZE_BYTES

        self._stats[STAT_READS] += 1
        return bytes(self._storage[start:end])


    def write_block_lba(self, lba: int, data: bytes):
        self._validate_block_id(lba)

        if len(data) != BLOCK_SIZE_BYTES:
            raise ValueError(f"Write must be exactly {BLOCK_SIZE_BYTES} bytes")

        # Overwrite handling
        if lba in self._lba_to_pba:
            old_pba = self._lba_to_pba[lba]
            self._block_states[old_pba] = BLOCK_TRIMMED

        pba = self._allocate_block()

        self._simulate_io_failure()

        start = pba * BLOCK_SIZE_BYTES
        end = start + BLOCK_SIZE_BYTES

        self._storage[start:end] = data
        self._block_states[pba] = BLOCK_USED

        self._lba_to_pba[lba] = pba
        self._pba_to_lba[pba] = lba

        self._stats[STAT_WRITES] += 1

    def trim_lba(self, lba: int):
        self._validate_block_id(lba)

        if lba in self._lba_to_pba:
            pba = self._lba_to_pba[lba]
            self._block_states[pba] = BLOCK_TRIMMED
            self._stats[STAT_TRIMS] += 1

    def mark_block_bad(self, block_id: int):
        self._validate_block_id(block_id)
        self._block_states[block_id] = BLOCK_BAD

    def get_stats(self) -> dict:
        return {
             "total_reads": self._stats[STAT_READS],
             "total_writes": self._stats[STAT_WRITES],
             "trim_operations": self._stats[STAT_TRIMS],
             "total_failures": self._stats[STAT_FAILURES],
        }



