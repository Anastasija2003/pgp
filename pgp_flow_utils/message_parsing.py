import struct
from datetime import datetime


def parse_message_packet(data: bytes):
    offset = 0
    filename_length = struct.unpack(">B", data[offset:offset + 1])[0]
    offset += 1
    filename = data[offset:offset + filename_length].decode("utf-8")
    offset += filename_length
    timestamp = datetime.fromtimestamp(struct.unpack(">I", data[offset:offset + 4])[0])
    offset += 4
    message_length = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    message_bytes = data[offset:offset + message_length]
    return filename, timestamp, message_bytes
