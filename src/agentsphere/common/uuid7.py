import os
import time
import uuid

_VAR_BITS_102 = 0b10 << 62
_VER_BITS_74851 = 0b0111 << 76


def uuid7() -> uuid.UUID:
    timestamp_ms = int(time.time() * 1000)
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") >> 2

    uuid_int = (timestamp_ms << 80) | (_VER_BITS_74851) | (rand_a << 64) | _VAR_BITS_102 | rand_b
    return uuid.UUID(int=uuid_int)
