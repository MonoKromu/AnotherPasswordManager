import base64

from cryptography.fernet import Fernet


def encrypt(password, key):
    key = base64.urlsafe_b64encode(bytes.fromhex(key))
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.hex()

def decrypt(encrypted_password, key):
    key = base64.urlsafe_b64encode(bytes.fromhex(key))
    fernet = Fernet(key)
    decrypted = fernet.decrypt(bytes.fromhex(encrypted_password))
    return decrypted.decode()