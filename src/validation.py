from __future__ import annotations

import base64
import binascii

from src.payload_encoder import crc16_ccitt_false


def verify_crc16(payload: bytes) -> bool:
    if len(payload) < 2:
        return False
    data = payload[:-2]
    expected = int.from_bytes(payload[-2:], "big", signed=False)
    return crc16_ccitt_false(data) == expected


def verify_base64_roundtrip(payload_b64: str) -> bool:
    try:
        decoded = base64.b64decode(payload_b64, validate=True)
    except (ValueError, binascii.Error):
        return False
    return base64.b64encode(decoded).decode("ascii") == payload_b64
