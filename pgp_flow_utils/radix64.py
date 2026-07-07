import base64

def convert_to_radix64(input: bytes):
    return base64.b64encode(input)

def convert_from_radix64(input: bytes):
    return base64.b64decode(input)