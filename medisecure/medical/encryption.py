import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.conf import settings


class AESService:
    @staticmethod
    def encrypt(data: str) -> str:
        if not data:
            return ""
        # En production, utilisez une clé sécurisée (ex: settings.SECRET_KEY)
        key = settings.SECRET_KEY[:32].encode()
        iv = (
            b"\x00" * 16
        )  # Simplifié pour la démo, utilisez un IV aléatoire en production
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Padding
        length = 16 - (len(data) % 16)
        data += chr(length) * length

        ct = encryptor.update(data.encode()) + encryptor.finalize()
        return base64.b64encode(ct).decode()

    @staticmethod
    def decrypt(enc_data: str) -> str:
        if not enc_data:
            return ""
        key = settings.SECRET_KEY[:32].encode()
        iv = b"\x00" * 16
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        ct = base64.b64decode(enc_data)
        data = decryptor.update(ct) + decryptor.finalize()

        # Unpadding
        data = data.decode()
        padding = ord(data[-1])
        return data[:-padding]
