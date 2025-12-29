from constants import BLOCK_SIZE_BYTES
from exceptions import OutOfBoundsError


class BlockDeviceDriver:

    def __init__(self, device):
        self.device = device

    def _check_bounds(self, offset: int, length: int):
        if offset < 0 or length < 0:
            raise OutOfBoundsError("Negative offset or length")

    def read(self, offset: int, length: int) -> bytes:
        self._check_bounds(offset, length)

        result = bytearray()
        start_lba = offset // BLOCK_SIZE_BYTES
        end_lba = (offset + length - 1) // BLOCK_SIZE_BYTES

        for lba in range(start_lba, end_lba + 1):
            block = self.device.read_block_lba(lba)
            result.extend(block)

        start = offset % BLOCK_SIZE_BYTES
        return bytes(result[start:start + length])

    def write(self, offset: int, data: bytes):
        self._check_bounds(offset, len(data))

        start_lba = offset // BLOCK_SIZE_BYTES
        end_lba = (offset + len(data) - 1) // BLOCK_SIZE_BYTES

        idx = 0
        for lba in range(start_lba, end_lba + 1):
            block = bytearray(self.device.read_block_lba(lba))

            block_offset = offset % BLOCK_SIZE_BYTES if lba == start_lba else 0
            write_len = min(
                BLOCK_SIZE_BYTES - block_offset,
                len(data) - idx
        )

        block[block_offset:block_offset + write_len] = data[idx:idx + write_len]

        self.device.write_block_lba(lba, bytes(block))
        idx += write_len


    def trim(self, offset: int, length: int):
        self._check_bounds(offset, length)

        start_lba = offset // BLOCK_SIZE_BYTES
        end_lba = (offset + length - 1) // BLOCK_SIZE_BYTES

        for lba in range(start_lba, end_lba + 1):
            self.device.trim_lba(lba)
     
     def get_lba_mapping(self, lba: int):
         return self.device._lba_to_pba.get(lba)


