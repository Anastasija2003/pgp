import os
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES as _TripleDESAlgorithm

from symetric_algorithms.SymetricAlgorithm import SymetricAlgorithm


class TripleDES(SymetricAlgorithm):
    IV_SIZE = 8

    def encrypt(self, input: bytes) -> bytes:
        iv = os.urandom(self.IV_SIZE)
        encryptor = Cipher(_TripleDESAlgorithm(self.key), modes.CFB(iv)).encryptor()
        ciphertext = encryptor.update(input)
        return iv + ciphertext

    def decrypt(self, input: bytes) -> bytes:
        iv = input[:self.IV_SIZE]
        ciphertext = input[self.IV_SIZE:]
        decryptor = Cipher(_TripleDESAlgorithm(self.key), modes.CFB(iv)).decryptor()
        return decryptor.update(ciphertext)
