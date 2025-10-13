import hashlib
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import MD4
import os

def derive_key(password: str) -> bytes:
    h = MD4.new()
    h.update(password.encode())
    return h.digest()[:8]

def encrypt_file(data: bytes, password: str) -> bytes:
    key = derive_key(password)
    iv = get_random_bytes(8)
    cipher = DES.new(key, DES.MODE_CFB, iv=iv)
    encrypted = cipher.encrypt(pad(data, DES.block_size))
    return iv + encrypted

def decrypt_file(data: bytes, password: str) -> bytes:
    key = derive_key(password)
    iv = data[:8]
    encrypted = data[8:]
    cipher = DES.new(key, DES.MODE_CFB, iv=iv)
    decrypted = unpad(cipher.decrypt(encrypted), DES.block_size)
    return decrypted