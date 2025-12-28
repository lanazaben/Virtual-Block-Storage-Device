from device import VirtualBlockDevice
from driver import BlockDeviceDriver
from constants import BLOCK_SIZE_BYTES


def main():
    print("Initializing virtual block device...")
    device = VirtualBlockDevice(simulate_failure=False)
    driver = BlockDeviceDriver(device)

    print("\n--- Basic Write / Read ---")
    data = b"Hello Block Device"
    driver.write(0, data)
    result = driver.read(0, len(data))
    print("Read:", result)

    print("\n--- Trim Demonstration ---")
    driver.trim(0, BLOCK_SIZE_BYTES)
    trimmed = driver.read(0, len(data))
    print("Trimmed read:", trimmed)

    print("\n--- LBA → Physical Mapping ---")
    for lba, pba in device._lba_to_pba.items():
        print(f"LBA {lba} -> Physical Block {pba}")

    print("\n--- Forcing Storage-Full Condition ---")
    lba = 1
    payload = b"A" * BLOCK_SIZE_BYTES

    try:
        while True:
            driver.write(lba * BLOCK_SIZE_BYTES, payload)
            lba += 1
    except Exception as e:
        print("Storage full detected:", str(e))

    print("\n--- Triggering Garbage Collection ---")
    print("Trimming half of the written blocks...")

    for i in range(1, lba, 2):
        driver.trim(i * BLOCK_SIZE_BYTES, BLOCK_SIZE_BYTES)

    print("Writing again to trigger GC...")
    driver.write(0, b"GC!")

    print("\n--- Post-GC Mapping ---")
    for lba, pba in device._lba_to_pba.items():
        print(f"LBA {lba} -> Physical Block {pba}")

    print("\n--- GC & Device Statistics ---")
    stats = device.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nDemo complete ✔")


if __name__ == "__main__":
    main()
