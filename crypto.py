import hashlib
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import MD4
import os

def derive_key(password: str, salt: bytes) -> bytes:
    # === Генерация ключа из пароля с использованием соли ===
    h = MD4.new()
    h.update(salt + password.encode())
    return h.digest()[:8]

def encrypt_file(data: bytes, password: str) -> bytes:
    # === Шифрование данных с использованием DES-CFB и случайной соли ===
    salt = get_random_bytes(8)
    key = derive_key(password, salt)
    iv = get_random_bytes(8)
    cipher = DES.new(key, DES.MODE_CFB, iv=iv)
    encrypted = cipher.encrypt(pad(data, DES.block_size))
    return salt + iv + encrypted

def decrypt_file(data: bytes, password: str) -> bytes:
    # === Расшифровка данных с использованием DES-CFB и соли из начала файла ===
    salt = data[:8]
    iv = data[8:16]
    encrypted = data[16:]
    key = derive_key(password, salt)
    cipher = DES.new(key, DES.MODE_CFB, iv=iv)
    decrypted = unpad(cipher.decrypt(encrypted), DES.block_size)
    return decrypted