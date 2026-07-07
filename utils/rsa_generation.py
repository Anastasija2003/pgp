from cryptography.hazmat.primitives.asymmetric import rsa
from keyring import PublicKeyring, PrivateKeyring

class KeysizeError(Exception):
    pass

def generateKeys(keysize, password, email, name, publicKeyring: PublicKeyring, privateKeyring: PrivateKeyring):
    if keysize != 1024 and keysize != 2048:
        raise KeysizeError("Keysize is either 1024 or 2048 bits")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=keysize
    )
    public_key = private_key.public_key()
    publicKeyring.add(public_key, email, name)
    privateKeyring.add(email, public_key, private_key, password, name)
    return public_key, private_key