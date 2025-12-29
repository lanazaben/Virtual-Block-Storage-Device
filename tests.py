import unittest

from device import VirtualBlockDevice
from constants import DEVICE_SIZE_BYTES
from driver import BlockDeviceDriver
from constants import BLOCK_SIZE_BYTES, TOTAL_BLOCKS
from exceptions import (
    InvalidBlockError,
    BadBlockError,
)


# Smoke Tests
class SmokeTests(unittest.TestCase):

    def test_device_initialization(self):
        device = VirtualBlockDevice()
        self.assertIsNotNone(device)

    def test_driver_initialization(self):
        device = VirtualBlockDevice()
        driver = BlockDeviceDriver(device)
        self.assertIsNotNone(driver)


# Black Box Tests
class BlackBoxTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_write_then_read(self):
        data = b"Hello"
        self.driver.write(0, data)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, data)

    def test_trim_then_read_returns_zeros(self):
        self.driver.write(0, b"ABC")
        self.driver.trim(0, BLOCK_SIZE_BYTES)
        result = self.driver.read(0, 3)
        self.assertEqual(result, b"\x00" * 3)

    def test_sequential_reads_writes(self):
        for lba in range(10):
            payload = f"data{lba}".encode()
            self.driver.write(lba, payload)
            result = self.driver.read(lba, len(payload))
            self.assertEqual(result[:len(payload)], payload)

    def test_statistics_update(self):
        stats_before = self.device.get_stats()

        self.driver.write(0, b"A")
        self.driver.read(0, 1)
        self.driver.trim(0, BLOCK_SIZE_BYTES)

        stats_after = self.device.get_stats()

        self.assertGreater(stats_after["total_reads"], stats_before["total_reads"])
        self.assertGreater(stats_after["total_writes"], stats_before["total_writes"])
        self.assertGreater(stats_after["trim_operations"], stats_before["trim_operations"])


# White Box Tests
class WhiteBoxTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_partial_block_write(self):
        data = b"A" * 10
        self.driver.write(0, data)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, data)

    def test_cross_block_write(self):
        data = b"B" * (BLOCK_SIZE_BYTES + 20)
        self.driver.write(0, data)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, data)

    def test_trimmed_block_reuse(self):
        self.driver.write(0, b"OLD")
        self.driver.trim(0, BLOCK_SIZE_BYTES)
        self.driver.write(0, b"NEW")
        result = self.driver.read(0, 3)
        self.assertEqual(result, b"NEW")


# Negative Tests
class NegativeTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_write_out_of_bounds(self):
        with self.assertRaises(InvalidBlockError):
            self.driver.write(TOTAL_BLOCKS + 1, b"A")

    def test_read_out_of_bounds(self):
        self.driver.write(DEVICE_SIZE_BYTES + 1, b"A")
        self.driver.read(DEVICE_SIZE_BYTES + 1, 10)

    def test_access_bad_block(self):
        # Force bad block to be allocated
        self.device.mark_block_bad(0)

        # Exhaust blocks until bad one is encountered
        self.driver.write(0, b"X")
        pba = self.driver.get_lba_mapping(0)
        self.device.mark_block_bad(pba)

        with self.assertRaises(BadBlockError):
            self.driver.read(0, 1)




# Stress Tests
class StressTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_many_writes_reads(self):
        for lba in range(min(500, TOTAL_BLOCKS)):
            data = f"pkt{lba}".encode()
            self.driver.write(lba, data)
            result = self.driver.read(lba, len(data))
            self.assertEqual(result[:len(data)], data)



if __name__ == "__main__":
    unittest.main()

