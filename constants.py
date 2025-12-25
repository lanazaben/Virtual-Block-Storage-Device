# Storage Configuration

DEVICE_SIZE_BYTES = 8 * 1024 * 1024

BLOCK_SIZE_BYTES = 4096

TOTAL_BLOCKS = DEVICE_SIZE_BYTES // BLOCK_SIZE_BYTES


# Block States

BLOCK_FREE = "FREE"

BLOCK_USED = "USED"

BLOCK_TRIMMED = "TRIMMED"

BLOCK_BAD = "BAD"


# Driver Configuration

MAX_WRITE_RETRIES = 3

# Logging Configuration

LOGGER_NAME = "virtual_block_device"

# Statistics Keys

STAT_READS = "total_reads"
STAT_WRITES = "total_writes"
STAT_TRIMS = "trim_operations"
STAT_FAILURES = "failed_operations"

