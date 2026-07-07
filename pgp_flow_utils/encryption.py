from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from symetric_algorithms.SymetricAlgorithm import SymetricAlgorithm
from symetric_algorithms.TripleDES import TripleDES
from symetric_algorithms.AES128 import AES128
import secrets
import struct

algorithms = {
    "AES128": AES128(),
    "3DES": TripleDES()
}

def generate_session_key(alg: str):
    if alg == "AES128":
        return secrets.token_bytes(16)
    if alg == "3DES":
        return secrets.token_bytes(24)
    raise ValueError("Algorithm not supported")

def construct_session_key_packet(key_id, encrypted_key: bytes, initial_value: bytes):
    packet = struct.pack(">Q", key_id)
    packet += struct.pack(">H", len(encrypted_key))
    packet += encrypted_key
    packet += initial_value
    return packet

def encrypt_message(session_key: bytes, algorithm: SymetricAlgorithm, input: bytes):
    algorithm.set_key(session_key)
    encrypted = algorithm.encrypt(input)
    return encrypted

def encrypt_session_key(session_key: bytes, public_rsa_key: rsa.RSAPublicKey):
    return public_rsa_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

def encrypt(input: bytes, public_key: rsa.RSAPublicKey, key_id, alg: str):
    session_key = generate_session_key(alg)
    current_algorithm = algorithms[alg]
    encrypted_input = encrypt_message(session_key, current_algorithm, input)
    iv_size = current_algorithm.IV_SIZE
    encrypted_message = encrypted_input[iv_size:]
    initial_value = encrypted_input[:iv_size]
    encrypted_session_key = encrypt_session_key(session_key, public_key)
    header_packet = construct_session_key_packet(key_id, encrypted_session_key, initial_value)
    return header_packet + encrypted_message
