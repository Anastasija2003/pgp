from pgp_flow_utils.message_header import get_message
from pgp_flow_utils.signature import sign
from pgp_flow_utils.compression import compress, decompress
from utils.rsa_generation import generateKeys
from keyring import PublicKeyring, PrivateKeyring
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

def decrypt_message_header(message_bytes:bytes, offset=0):
    #offset = 0
    duzina = int.from_bytes(message_bytes[:1], byteorder="big")
    print(duzina)
    offset += 1
    filename = message_bytes[offset:offset+duzina].decode("utf-8")
    print(filename)
    offset += duzina
    timestamp_bytes = message_bytes[offset:offset+4]
    offset += 4
    timestamp_int = int.from_bytes(timestamp_bytes, byteorder="big")
    print(datetime.fromtimestamp(float(timestamp_int)))
    data_length = int.from_bytes(message_bytes[offset:offset+4], byteorder="big")
    offset += 4
    print(data_length)
    message_content = message_bytes[offset:offset+data_length].decode("utf-8")
    print(message_content)
    return

def hash_message(message_packet):
    hash_fun = hashes.Hash(hashes.SHA1())
    hash_fun.update(message_packet)
    return hash_fun.finalize()

def decrypt_signature(message_bytes: bytes, public_key: rsa.RSAPublicKey):
    offset = 0
    timestamp = message_bytes[offset:offset+4]
    offset += 4
    key_id = message_bytes[offset:offset+8]
    offset += 8
    octets = message_bytes[offset:offset+2]
    offset += 2
    sign_len = message_bytes[offset:offset+2]
    sign_len = int.from_bytes(sign_len, byteorder="big")
    offset += 2
    encrypted_sign = message_bytes[offset:offset+sign_len]
    offset += sign_len
    message = message_bytes[offset:]
    hash = hash_message(message)


    try:
        public_key.verify(
            encrypted_sign,
            hash,
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA1())
        )
        print("Signature valid")
    except InvalidSignature:
        print("Signature invalid")


def generateKeyID(publicKey):
    n = publicKey.public_numbers().n
    key_id_int = n & 0xFFFFFFFFFFFFFFFF
    return key_id_int

publicKeyring = PublicKeyring()
privateKeyring = PrivateKeyring()

public, private = generateKeys(1024, "lozinka1", "velja", "kljuc1", publicKeyring, privateKeyring)

message = "Ovo je poruka!"
message_packet = get_message(message)
hash = sign(message_packet, generateKeyID(public),private)
compressed = compress(hash)

print(message)
print(message.encode("utf-8"))
print(message_packet)
print(hash)
print(len(hash))
decrypt_message_header(message_packet)
decrypt_signature(hash, public)
print(compressed)
print(decompress(compressed))
print(len(compressed))
print(len(hash))
print(hash == decompress(compressed))