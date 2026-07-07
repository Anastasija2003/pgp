from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generateKeyID(publicKey):
    n = publicKey.public_numbers().n
    key_id_int = n & 0xFFFFFFFFFFFFFFFF
    return key_id_int

class PublicKeyEntry:
    def __init__(self, publicKey, email, keyID, givenName=None):
        self.timestamp = datetime.now()
        self.public_key : rsa.RSAPublicKey = publicKey
        self.user_id  = email
        self.key_id = keyID
        self.given_name = givenName

    def get_user_id(self):
        return self.user_id

    def get_public_key_pem(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

class PublicKeyring:
    def __init__(self):
        self.hash_map_key_id = dict()
        self.hash_map_user_id = dict()

    def add(self, publicKey, email, name):
        entry = PublicKeyEntry(publicKey, email, generateKeyID(publicKey), name)
        self.hash_map_user_id.setdefault(email, []).append(entry)
        self.hash_map_key_id[generateKeyID(publicKey)] = entry


    def remove(self, keyID):
        entry = self.hash_map_key_id.pop(keyID, None)
        if entry is None:
            return

        userID = entry.get_user_id()
        entries_for_user = self.hash_map_user_id.get(userID, [])
        entries_for_user[:] = [e for e in entries_for_user if e.key_id != keyID]

        if not entries_for_user:
            self.hash_map_user_id.pop(userID, None)

    def getAll(self):
        return self.hash_map_key_id.values()



class PrivateKeyringEntry:
    def __init__(self, keyID, publicKey: rsa.RSAPublicKey, userID, privateKey: rsa.RSAPrivateKey, password: str,
                 givenName=None):
        self.timestamp = datetime.now()
        self.key_id = keyID
        self.public_key = publicKey
        self.user_id = userID
        self.given_name = givenName
        self.encrypted_private_key = privateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password.encode("utf-8")
            )
        )

    def get_private_key(self, password:str): # baca ValueError ako se pogresi lozinka
       return serialization.load_pem_private_key(
           self.encrypted_private_key,
           password=password.encode("utf-8")
       )

    def get_encrypted_private_key_pem(self) -> str:
        return self.encrypted_private_key.decode("utf-8")

    def get_public_key_pem(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def get_user_id(self):
        return self.user_id

class PrivateKeyring:
    def __init__(self):
        self.hash_map_key_id = dict()
        self.hash_map_user_id = dict()

    def add(self, userID, publicKey, privateKey, password, name):
        key_id = generateKeyID(publicKey)
        entry = PrivateKeyringEntry(key_id, publicKey, userID, privateKey, password, name)

        self.hash_map_key_id[key_id] = entry
        self.hash_map_user_id.setdefault(userID, []).append(entry)

    def remove(self, keyID):
        entry = self.hash_map_key_id.pop(keyID, None)
        if entry is None:
            return

        userID = entry.get_user_id()
        entries_for_user = self.hash_map_user_id.get(userID, [])
        entries_for_user[:] = [e for e in entries_for_user if e.key_id != keyID]

        if not entries_for_user:
            self.hash_map_user_id.pop(userID, None)

    def getAll(self):
        return self.hash_map_key_id.values()
