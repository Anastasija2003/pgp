from cryptography.hazmat.primitives.asymmetric import rsa
from symetric_algorithms.SymetricAlgorithm import SymetricAlgorithm
import secrets

def generate_session_key(alg: str):
    if alg == "AES128":
        return secrets.token_bytes(16)
    if alg == "3DES":
        return secrets.token_bytes(24)
    raise ValueError("Algorithm not supported")

def generate_initial_value():
    return secrets.token_bytes(16)

def construct_session_key_packet():
    pass

def encrypt_message(session_key: bytes, algorithm: SymetricAlgorithm, input: bytes):
    algorithm.set_key(session_key)
    encrypted = algorithm.encrypt(input)
    return encrypted

def encrypt_session_key(session_key: bytes, public_rsa_key: rsa.RSAPublicKey):
    pass

def encrypt(input: bytes, public_key: rsa.RSAPublicKey, key_id):
    pass
