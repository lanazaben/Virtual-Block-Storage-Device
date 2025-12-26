from constants import (
    BLOCK_SIZE_BYTES,
    DEVICE_SIZE_BYTES,
    MAX_WRITE_RETRIES,
    BLOCK_TRIMMED,
)

from exceptions import (
    OutOfBoundsError,
    BadBlockError,
    DeviceIOError,
    WriteRetryExceededError,
    TrimmedBlockReadError,
)

from device import VirtualBlockDevice


class BlockDeviceDriver:

    def __init__(self, device: VirtualBlockDevice):
        self.device = device

    # Validation Helpers

    def _validate_bounds(self, offset: int, size: int):
        if offset < 0 or size < 0:
            raise OutOfBoundsError("Offset and size must be non-negative")

        if offset + size > DEVICE_SIZE_BYTES:
            raise OutOfBoundsError("Operation exceeds device size")

    def _zero_block(self) -> bytes:
        return bytes(BLOCK_SIZE_BYTES)

    # Public Driver Interface

    def read(self, offset: int, size: int) -> bytes:
        self._validate_bounds(offset, size)

        if size == 0:
            return b""

        result = bytearray()

        while size > 0:
            block_id = offset // BLOCK_SIZE_BYTES
            block_offset = offset % BLOCK_SIZE_BYTES

            bytes_available = BLOCK_SIZE_BYTES - block_offset
            bytes_to_read = min(size, bytes_available)

            try:
                block_data = self.device.read_block(block_id)
            except TrimmedBlockReadError:
                # Trimmed blocks are treated as zero-filled
                block_data = self._zero_block()

            chunk = block_data[block_offset:block_offset + bytes_to_read]
            result.extend(chunk)

            offset += bytes_to_read
            size -= bytes_to_read

        return bytes(result)

    def write(self, offset: int, data: bytes):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")

        size = len(data)
        self._validate_bounds(offset, size)

        data_offset = 0

        while size > 0:
            block_id = offset // BLOCK_SIZE_BYTES
            block_offset = offset % BLOCK_SIZE_BYTES

            bytes_available = BLOCK_SIZE_BYTES - block_offset
            bytes_to_write = min(size, bytes_available)

            # Read existing block to preserve unaffected regions
            try:
                try:
                    block_data = self.device.read_block(block_id)
                except TrimmedBlockReadError:
                    block_data = self._zero_block()

                block_buffer = bytearray(block_data)

                block_buffer[
                    block_offset:block_offset + bytes_to_write
                ] = data[data_offset:data_offset + bytes_to_write]

            except BadBlockError:
                # Writing to a bad block is not recoverable
                raise

            # Retry loop for recoverable I/O failures
            for attempt in range(MAX_WRITE_RETRIES):
                try:
                    self.device.write_block(block_id, bytes(block_buffer))
                    break
                except DeviceIOError:
                    if attempt == MAX_WRITE_RETRIES - 1:
                        raise WriteRetryExceededError(
                            f"Write failed after {MAX_WRITE_RETRIES} retries"
                        )
                    # Retry silently; device-level failures are expected

            offset += bytes_to_write
            data_offset += bytes_to_write
            size -= bytes_to_write

    def trim(self, offset: int, size: int):

        self._validate_bounds(offset, size)

        if size == 0:
            return

        start_block = offset // BLOCK_SIZE_BYTES
        end_block = (offset + size - 1) // BLOCK_SIZE_BYTES

        for block_id in range(start_block, end_block + 1):
            self.device.trim_block(block_id)

