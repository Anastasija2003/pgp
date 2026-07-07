import struct
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

from pgp_flow_utils.signature import hash_message


def parse_signature_packet(data: bytes):
    offset = 0
    timestamp = datetime.fromtimestamp(struct.unpack(">I", data[offset:offset + 4])[0])
    offset += 4
    key_id = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8
    leading_octets = data[offset:offset + 2]
    offset += 2
    encrypted_length = struct.unpack(">H", data[offset:offset + 2])[0]
    offset += 2
    encrypted_hash = data[offset:offset + encrypted_length]
    offset += encrypted_length
    message_packet = data[offset:]
    return timestamp, key_id, leading_octets, encrypted_hash, message_packet


def verify(message_packet: bytes, encrypted_hash: bytes, leading_octets: bytes,
           public_key: rsa.RSAPublicKey) -> bool:
    computed_hash = hash_message(message_packet)

    if computed_hash[:2] != leading_octets:
        return False

    try:
        public_key.verify(
            encrypted_hash,
            computed_hash,
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA1()),
        )
        return True
    except InvalidSignature:
        return False
