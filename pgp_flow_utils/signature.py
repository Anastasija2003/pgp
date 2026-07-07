from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa
import struct


def hash_message(message_packet):
    hash_fun = hashes.Hash(hashes.SHA1())
    hash_fun.update(message_packet)
    return hash_fun.finalize()


def encrypt_with_private_key(message_hash, private_key: rsa.RSAPrivateKey):
    return private_key.sign(
        data=message_hash,
        padding=padding.PKCS1v15(),
        algorithm=utils.Prehashed(hashes.SHA1())
    )


def signature_packet(key_id, leading_octets, encrypted_hash, encrypted_length, timestamp):
    packet = struct.pack(">I", int(timestamp.timestamp()))
    packet += struct.pack(">Q", key_id)
    packet += leading_octets
    packet += struct.pack(">H", encrypted_length)
    packet += encrypted_hash
    return packet


def sign(message_packet, key_id, private_key):
    message_hash = hash_message(message_packet)
    leading_2_octets = message_hash[:2]
    encrypted_hash = encrypt_with_private_key(message_hash, private_key)
    encrypted_length = len(encrypted_hash)
    sign_packet = signature_packet(key_id, leading_2_octets, encrypted_hash, encrypted_length, datetime.now())
    signed_message = sign_packet + message_packet
    return signed_message
