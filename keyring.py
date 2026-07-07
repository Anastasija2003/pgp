import json
import os
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

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "given_name": self.given_name,
            "timestamp": self.timestamp.isoformat(),
            "public_key_pem": self.get_public_key_pem(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicKeyEntry":
        public_key = serialization.load_pem_public_key(data["public_key_pem"].encode("utf-8"))
        entry = cls(public_key, data["user_id"], data["key_id"], data.get("given_name"))
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        return entry

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

    def save(self, path):
        entries = [entry.to_dict() for entry in self.hash_map_key_id.values()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def load(self, path):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for data in entries:
            entry = PublicKeyEntry.from_dict(data)
            self.hash_map_key_id[entry.key_id] = entry
            self.hash_map_user_id.setdefault(entry.user_id, []).append(entry)



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

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "given_name": self.given_name,
            "timestamp": self.timestamp.isoformat(),
            "public_key_pem": self.get_public_key_pem(),
            "encrypted_private_key_pem": self.get_encrypted_private_key_pem(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PrivateKeyringEntry":
        entry = cls.__new__(cls)
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        entry.key_id = data["key_id"]
        entry.public_key = serialization.load_pem_public_key(data["public_key_pem"].encode("utf-8"))
        entry.user_id = data["user_id"]
        entry.given_name = data.get("given_name")
        entry.encrypted_private_key = data["encrypted_private_key_pem"].encode("utf-8")
        return entry

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

    def save(self, path):
        entries = [entry.to_dict() for entry in self.hash_map_key_id.values()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def load(self, path):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for data in entries:
            entry = PrivateKeyringEntry.from_dict(data)
            self.hash_map_key_id[entry.key_id] = entry
            self.hash_map_user_id.setdefault(entry.user_id, []).append(entry)
