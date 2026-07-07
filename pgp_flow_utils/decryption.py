import struct

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


def decrypt_session_key(encrypted_session_key: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        ),
    )


def parse_session_key_packet(data: bytes, iv_size: int):
    offset = 0
    key_id = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8
    encrypted_key_length = struct.unpack(">H", data[offset:offset + 2])[0]
    offset += 2
    encrypted_session_key = data[offset:offset + encrypted_key_length]
    offset += encrypted_key_length
    initial_value = data[offset:offset + iv_size]
    offset += iv_size
    rest = data[offset:]
    return key_id, encrypted_session_key, initial_value, rest
