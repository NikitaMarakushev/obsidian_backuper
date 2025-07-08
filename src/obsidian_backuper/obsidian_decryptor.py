import os
from typing import Optional
from .exceptions import (
    ArchiveError,
    DecryptionError
)
from .crypto import CryptoVault


class ObsidianDecryptor:
    def __init__(self, encrypted_file_path: str):
        self.encrypted_file_path = self._validate_encrypted_file(encrypted_file_path)

    def _validate_encrypted_file(self, path: str) -> str:
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            raise ArchiveError(f"Encrypted file not found at {expanded_path}")
        if not os.path.isfile(expanded_path):
            raise ArchiveError(f"Path is not a file: {expanded_path}")
        if not expanded_path.endswith('.enc'):
            raise ArchiveError("File must have .enc extension for decryption")
        return expanded_path

    def decrypt(self, password: str, output_dir: Optional[str] = None) -> str:
        try:
            if output_dir is None:
                output_dir = os.path.dirname(os.path.abspath(self.encrypted_file_path))

            decrypted_name = os.path.basename(self.encrypted_file_path).replace('.enc', '')
            final_path = os.path.join(output_dir, decrypted_name)

            crypto = CryptoVault(password)
            crypto.decrypt_file(self.encrypted_file_path, final_path)

            return final_path
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")