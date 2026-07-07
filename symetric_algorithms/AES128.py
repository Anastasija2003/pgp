import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from symetric_algorithms.SymetricAlgorithm import SymetricAlgorithm


class AES128(SymetricAlgorithm):
    IV_SIZE = 16

    def encrypt(self, input: bytes) -> bytes:
        iv = secrets.token_bytes(self.IV_SIZE)
        encryptor = Cipher(algorithms.AES128(self.key), modes.CFB(iv)).encryptor()
        ciphertext = encryptor.update(input)
        return iv + ciphertext

    def decrypt(self, input: bytes) -> bytes:
        iv = input[:self.IV_SIZE]
        ciphertext = input[self.IV_SIZE:]
        decryptor = Cipher(algorithms.AES128(self.key), modes.CFB(iv)).decryptor()
        return decryptor.update(ciphertext)
