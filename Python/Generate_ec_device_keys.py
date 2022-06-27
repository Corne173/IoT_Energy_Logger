from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_ec_keys():
    # create a private EC key
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    # get private key value and write to file
    private_key_bytes = bytes.fromhex(format(private_key.private_numbers().private_value, '064x')) #converts int to hex
    list_of_bytes = list(map(hex, list(private_key_bytes)))     # creates list of bytes
    ESP_private_key = ",".join(list_of_bytes)                   # comma separates each byte
    with open("ESP_private_key.txt", "w") as file:
        file.write(ESP_private_key)
    print(f"ESP private key:\n {ESP_private_key}\n")

    # write private PEM to file
    with open('ec_private.pem', 'wb') as filekey:
        filekey.write(private_pem)
    print(private_pem.decode("utf-8"))

    # generate public EC key from private key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)

    # write public PEM to file
    with open('ec_public.pem', 'wb') as filekey:
        filekey.write(public_pem)
    print(public_pem.decode("utf-8"))

if __name__ == "__main__":
    generate_ec_keys()
