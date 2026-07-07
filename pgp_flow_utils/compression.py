import zlib

def compress(input: bytes):
    return zlib.compress(input)

def decompress(input: bytes):
    return zlib.decompress(input)