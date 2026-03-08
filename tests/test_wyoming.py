"""Tests for Wyoming protocol encoding (no server import)."""

import json

from wyoming_protocol import encode_message


def test_encode_message_empty_data_no_payload():
    raw = encode_message("info", {})
    idx = raw.index(b"\n")
    line = raw[:idx].decode("utf-8")
    rest_bytes = raw[idx + 1 :]
    obj = json.loads(line)
    assert obj["type"] == "info"
    assert obj["data_length"] == 2  # "{}"
    assert obj["payload_length"] == 0
    assert rest_bytes == b"{}"


def test_encode_message_with_data_and_payload():
    data = {"rate": 24000, "width": 2, "channels": 1}
    payload = b"\x00\x01\x02"
    raw = encode_message("audio-chunk", data, payload)
    idx = raw.index(b"\n")
    line = raw[:idx].decode("utf-8")
    rest_bytes = raw[idx + 1 :]
    obj = json.loads(line)
    assert obj["type"] == "audio-chunk"
    assert obj["payload_length"] == 3
    data_len = obj["data_length"]
    data_bytes = rest_bytes[:data_len]
    parsed_data = json.loads(data_bytes.decode("utf-8"))
    assert parsed_data == data
    assert rest_bytes[data_len:] == payload


def test_encode_message_roundtrip_data():
    data = {"text": "Hello", "voice": {"name": "test"}}
    raw = encode_message("synthesize", data)
    idx = raw.index(b"\n")
    line = raw[:idx].decode("utf-8")
    rest_bytes = raw[idx + 1 :]
    header = json.loads(line)
    data_bytes = rest_bytes[: header["data_length"]]
    decoded = json.loads(data_bytes.decode("utf-8"))
    assert decoded == data
