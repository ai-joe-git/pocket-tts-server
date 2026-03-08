"""
Wyoming protocol encoding (Home Assistant TTS).
Used by pocket_tts_api for Wyoming TCP messages.
"""

import json


def encode_message(msg_type: str, data: dict, payload: bytes = b"") -> bytes:
    """Encode one Wyoming protocol message.
    Matches Wyoming package: line has data_length (data bytes), then payload.
    """
    data = dict(data) if data else {}
    data_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    header_obj = {
        "type": msg_type,
        "data_length": len(data_bytes),
        "payload_length": len(payload),
    }
    header = json.dumps(header_obj) + "\n"
    return header.encode("utf-8") + data_bytes + payload
