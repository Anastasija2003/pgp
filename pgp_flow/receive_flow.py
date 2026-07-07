from pgp_flow_utils.radix64 import convert_from_radix64
from pgp_flow_utils.decryption import parse_session_key_packet, decrypt_session_key
from pgp_flow_utils.compression import decompress
from pgp_flow_utils.verification import parse_signature_packet, verify
from pgp_flow_utils.message_parsing import parse_message_packet
from symetric_algorithms.AES128 import AES128
from symetric_algorithms.TripleDES import TripleDES

FLAG_SIGNATURE = 1 << 0
FLAG_COMPRESSION = 1 << 1
FLAG_ENCRYPTION = 1 << 2
FLAG_RADIX64 = 1 << 3
FLAG_TRIPLEDES = 1 << 4
FLAG_AES128 = 1 << 5


class UnknownKeyError(Exception):
    def __init__(self, key_id):
        super().__init__(f"Nepoznat key_id: {key_id}")
        self.key_id = key_id


class ReceiveContext:
    def __init__(self, flags, payload, encrypted_session_key=None, iv=None, private_key_entry=None):
        self.flags = flags
        self.payload = payload
        self.encrypted_session_key = encrypted_session_key
        self.iv = iv
        self.private_key_entry = private_key_entry

    def needs_password(self):
        return self.private_key_entry is not None


def start_receive(file_bytes: bytes, private_keyring) -> ReceiveContext:
    flags = file_bytes[0]
    payload = file_bytes[1:]

    if flags & FLAG_RADIX64:
        payload = convert_from_radix64(payload)

    if not (flags & FLAG_ENCRYPTION):
        return ReceiveContext(flags, payload)

    iv_size = AES128.IV_SIZE if flags & FLAG_AES128 else TripleDES.IV_SIZE
    key_id, encrypted_session_key, iv, rest = parse_session_key_packet(payload, iv_size)

    entry = private_keyring.hash_map_key_id.get(key_id)
    if entry is None:
        raise UnknownKeyError(key_id)

    return ReceiveContext(flags, rest, encrypted_session_key, iv, entry)


def finish_receive(context: ReceiveContext, password: str, public_keyring):
    payload = context.payload

    if context.needs_password():
        private_key = context.private_key_entry.get_private_key(password)
        session_key = decrypt_session_key(context.encrypted_session_key, private_key)
        algorithm = AES128() if context.flags & FLAG_AES128 else TripleDES()
        algorithm.set_key(session_key)
        payload = algorithm.decrypt(context.iv + payload)

    if context.flags & FLAG_COMPRESSION:
        payload = decompress(payload)

    signer_entry = None
    signature_valid = None
    if context.flags & FLAG_SIGNATURE:
        timestamp, key_id, leading_octets, encrypted_hash, payload = parse_signature_packet(payload)
        signer_entry = public_keyring.hash_map_key_id.get(key_id)
        if signer_entry is None:
            raise UnknownKeyError(key_id)
        signature_valid = verify(payload, encrypted_hash, leading_octets, signer_entry.public_key)

    filename, timestamp, message_bytes = parse_message_packet(payload)

    return filename, message_bytes, signer_entry, signature_valid
