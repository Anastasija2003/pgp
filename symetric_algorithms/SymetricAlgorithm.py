class SymetricAlgorithm:
    def __init__(self, key=None):
        self.key = key

    def set_key(self, key: bytes):
        self.key = key

    def encrypt(self, input: bytes):
        pass

    def decrypt(self, input: bytes):
        pass
