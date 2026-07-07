from pgp_flow_utils.message_header import get_message
from pgp_flow_utils.signature import sign
from pgp_flow_utils.compression import compress
from pgp_flow_utils.encryption import encrypt
from pgp_flow_utils.radix64 import convert_to_radix64
import struct

algorithm_codes = {
    "3DES": (1<<4),
    "AES128": (1<<5)
}


def construct_message(message: str, signed: bool, compressed: bool, encrypted: bool, radix64: bool, algorithm: str,
                      private_key_sign, public_key_encrypt, sign_key_id, encrypt_key_id):

    header_byte = 0
    output_bytes = get_message(message)
    if signed == True:
        header_byte |= 1
        output_bytes = sign(output_bytes, sign_key_id, private_key_sign)
    if compressed == True:
        header_byte |= (1<<1)
        output_bytes = compress(output_bytes)
    if encrypted == True:
        header_byte |= (1<<2)
        header_byte |= algorithm_codes[algorithm]
        output_bytes = encrypt(output_bytes, public_key_encrypt, encrypt_key_id, algorithm)
    if radix64 == True:
        header_byte |= (1<<3)
        output_bytes = convert_to_radix64(output_bytes)

    final_message = struct.pack(">B", header_byte)
    final_message += output_bytes
    return final_message


def send_message(out_path, message: str, options, algorithm, private_key=None, public_key=None,
                 sign_key_id=None, encrypt_key_id=None):
    final_message = construct_message(message, options["signed"], options["compressed"], options["encrypted"],
                                      options["radix"], algorithm, private_key, public_key, sign_key_id, encrypt_key_id)
    with open(out_path, "wb") as f:
        f.write(final_message)
