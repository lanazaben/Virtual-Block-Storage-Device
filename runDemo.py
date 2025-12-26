# runDemo.py

from device import VirtualBlockDevice
from driver import BlockDeviceDriver
from exceptions import DeviceError

def main():
    device = VirtualBlockDevice()
    driver = BlockDeviceDriver(device)

    try:
        print("Writing data...")
        driver.write(1000, b"Hello Block Device")

        print("Reading data...")
        data = driver.read(1000, len(b"Hello Block Device"))
        print("Read:", data)

        print("Trimming first block...")
        driver.trim(0, 4096)

        print("Reading trimmed block...")
        trimmed_data = driver.read(0, 16)
        print("Trimmed read:", trimmed_data)

    except DeviceError as e:
        print("Device error occurred:", e)

    finally:
        print("Device stats:")
        print(device.get_stats())

if __name__ == "__main__":
    main()
#
