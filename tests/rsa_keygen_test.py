from rsa_generation import generateKeys
from keyring import PublicKeyring, PrivateKeyring

publicKeyring = PublicKeyring()
privateKeyring = PrivateKeyring()

generateKeys(1024, "lozinka1", "velja", "kljuc1", publicKeyring, privateKeyring)
generateKeys(2048, "lozinka2", "tasa", "kljuc2", publicKeyring, privateKeyring)

publics = publicKeyring.getAll()
privates = privateKeyring.getAll()

for entry in publics:
    print(f"{entry.user_id} {entry.key_id} {entry.given_name} {entry.public_key}")

print("############################################################################")

for entry in privates:
    print(f"{entry.user_id} {entry.key_id} {entry.given_name} {entry.encrypted_private_key}")

print("############################################################################")

print("TEST LOZINKE")

try:
    for entry in privates:
        print(entry.get_private_key("lozinka1"))
except ValueError:
    print("Pogresna lozinka")