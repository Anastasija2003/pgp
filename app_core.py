from keyring import PublicKeyring, PrivateKeyring

PUBLIC_KEYRING_PATH = "public_keyring.json"
PRIVATE_KEYRING_PATH = "private_keyring.json"

publicKeyring = PublicKeyring()
privateKeyring = PrivateKeyring()

publicKeyring.load(PUBLIC_KEYRING_PATH)
privateKeyring.load(PRIVATE_KEYRING_PATH)


def save_keyrings():
    publicKeyring.save(PUBLIC_KEYRING_PATH)
    privateKeyring.save(PRIVATE_KEYRING_PATH)


def delete_key(key_id):
    publicKeyring.remove(key_id)
    privateKeyring.remove(key_id)