import unittest

from device import VirtualBlockDevice
from driver import BlockDeviceDriver
from constants import BLOCK_SIZE_BYTES, DEVICE_SIZE_BYTES
from exceptions import (
    OutOfBoundsError,
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
        data = b"Hello Block Device"
        self.driver.write(0, data)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, data)

    def test_trim_then_read_returns_zeros(self):
        data = b"ABCDEF"
        self.driver.write(0, data)
        self.driver.trim(0, BLOCK_SIZE_BYTES)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, b"\x00" * len(data))

    def test_sequential_reads_writes(self):
        for i in range(10):
            payload = f"data{i}".encode()
            offset = i * 100
            self.driver.write(offset, payload)
            result = self.driver.read(offset, len(payload))
            self.assertEqual(result, payload)

    def test_statistics_update(self):
        initial = self.device.get_stats()

        self.driver.write(0, b"A")
        self.driver.read(0, 1)
        self.driver.trim(0, BLOCK_SIZE_BYTES)

        stats = self.device.get_stats()

        self.assertGreaterEqual(
            stats["total_reads"],
            initial["total_reads"] + 1
        )
        self.assertGreaterEqual(
            stats["total_writes"],
            initial["total_writes"] + 1
        )
        self.assertGreaterEqual(
            stats["trim_operations"],
            initial["trim_operations"] + 1
        )


# White Box Tests
class WhiteBoxTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_partial_block_write(self):
        data = b"A" * (BLOCK_SIZE_BYTES // 2)
        self.driver.write(0, data)
        result = self.driver.read(0, len(data))
        self.assertEqual(result, data)

    def test_cross_block_write(self):
        data = b"B" * (BLOCK_SIZE_BYTES + 10)
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
        with self.assertRaises(OutOfBoundsError):
            self.driver.write(DEVICE_SIZE_BYTES + 1, b"A")

    def test_read_out_of_bounds(self):
        with self.assertRaises(OutOfBoundsError):
            self.driver.read(DEVICE_SIZE_BYTES + 1, 10)

    def test_access_bad_block(self):
        self.device.mark_block_bad(0)
        with self.assertRaises(BadBlockError):
            self.driver.write(0, b"X")


# Stress Tests
class StressTests(unittest.TestCase):

    def setUp(self):
        self.device = VirtualBlockDevice(simulate_failure=False)
        self.driver = BlockDeviceDriver(self.device)

    def test_many_writes_reads(self):
        for i in range(1000):
            offset = (i * 10) % (DEVICE_SIZE_BYTES - 20)
            data = f"pkt{i}".encode()
            self.driver.write(offset, data)
            result = self.driver.read(offset, len(data))
            self.assertEqual(result, data)


if __name__ == "__main__":
    unittest.main()


