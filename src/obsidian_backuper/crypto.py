import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from .exceptions import EncryptionError


class CryptoVault:
    def __init__(self, password: str, salt: bytes = None):
        if not password:
            raise EncryptionError("Password cannot be empty")
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password)

    def _derive_key(self, password: str) -> bytes:
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=480000,
                backend=default_backend()
            )
            return base64.urlsafe_b64encode(kdf.derive(password.encode()))
        except Exception as e:
            raise EncryptionError(f"Key derivation failed: {str(e)}")

    def encrypt_file(self, input_path: str, output_path: str):
        try:
            if not os.path.exists(input_path):
                raise EncryptionError(f"Input file not found: {input_path}")

            fernet = Fernet(self.key)
            with open(input_path, 'rb') as f:
                data = f.read()

            encrypted = fernet.encrypt(data)

            with open(output_path, 'wb') as f:
                f.write(self.salt + encrypted)

        except (IOError, InvalidToken) as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")

    def decrypt_file(self, input_path: str, output_path: str, password: str):
        try:
            if not os.path.exists(input_path):
                raise EncryptionError(f"Encrypted file not found: {input_path}")

            with open(input_path, 'rb') as f:
                salt = f.read(16)
                encrypted = f.read()

            self.salt = salt
            self.key = self._derive_key(password)

            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(encrypted)

            with open(output_path, 'wb') as f:
                f.write(decrypted)

        except InvalidToken:
            raise EncryptionError("Invalid password or corrupted file")
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")