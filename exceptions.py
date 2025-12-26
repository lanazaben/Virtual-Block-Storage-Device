class DeviceError(Exception):
    pass


# Addressing & Bounds Errors

class OutOfBoundsError(DeviceError):
    pass


class InvalidBlockError(DeviceError):
    pass


# Block State Errors

class BadBlockError(DeviceError):
    pass


class TrimmedBlockReadError(DeviceError):
    pass


# I/O & Write Errors

class DeviceIOError(DeviceError):
    pass


class PartialWriteError(DeviceError):
    pass


class WriteRetryExceededError(DeviceError):
    pass

