from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# a = "83:81:21:57:e8:0f:63:6b:53:d1:40:e7:27:b8:a6:94:a3:fd:ad:bb:e6:0f:b0:33:a1:f0:d1:f0:a1:99:0b:29"
# print(",0x".join(a.split(":")))

def generate_ec_keys():
    private_key = ec.generate_private_key(ec.SECP256R1()) #P-256
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('../ec_private.pem', 'wb') as filekey:
        filekey.write(private_pem)
    print(private_pem.decode("utf-8"))

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
       encoding=serialization.Encoding.PEM,
       format=serialization.PublicFormat.SubjectPublicKeyInfo)

    with open('../ec_public.pem', 'wb') as filekey:
        filekey.write(public_pem)
    print(public_pem.decode("utf-8"))


    shared_key = private_key.exchange(
        ec.ECDH(), private_key.public_key())
    # Perform key derivation.
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=None,
    ).derive(shared_key)

    shared_hex_keys = list(map(hex,list(derived_key)))
    with open("../shared_hex_keys.txt", "w") as file:
        data = ",".join(shared_hex_keys)
        file.write(data)
    print(f"Device key:\n {data}")

if __name__ == "__main__":
    generate_ec_keys()
