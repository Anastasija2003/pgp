from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def export_public_key(public_key: rsa.RSAPublicKey, file_address):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(file_address, "wb") as f:
        f.write(pem)

def export_private_key(encrypted_private_key, file_address):
    with open(file_address, "wb") as f:
        f.write(encrypted_private_key)

def import_public_key(file_address):
    print(file_address)
    with open(file_address, "rb") as f:
        pem = f.read()
    public_key = serialization.load_pem_public_key(pem)
    return public_key

def import_private_key(file_address, password):
    with open(file_address, "rb") as f:
        pem = f.read()
    private_key = serialization.load_pem_private_key(pem, password=password.encode("utf-8"))
    return private_key