import struct
from datetime import datetime

def construct_message_packet(message_bytes, filename_bytes, timestamp):
    filename_length = len(filename_bytes)
    message_length = len(message_bytes)

    packet = struct.pack(">B", filename_length)
    packet += filename_bytes
    packet += struct.pack(">I", int(timestamp.timestamp()))
    packet += struct.pack(">I", message_length)
    packet += message_bytes
    return packet

def get_message(message: str):
    message_bytes = message.encode("utf-8")
    filename_bytes = "poruka.txt".encode("utf-8")
    timestamp = datetime.now()
    return construct_message_packet(message_bytes, filename_bytes, timestamp)