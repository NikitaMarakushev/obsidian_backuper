import os
import tarfile
import tempfile
from datetime import datetime
from typing import Optional
from .exceptions import (
    VaultValidationError,
    EncryptionError,
    ArchiveError, ObsidianBackupError
)
from .crypto import CryptoVault


class ObsidianBackuper:
    def __init__(self, vault_path: str, remote_url: Optional[str] = None):
        self.vault_path = self._validate_vault_path(vault_path)
        self.remote_url = remote_url

    def _validate_vault_path(self, path: str) -> str:
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            raise VaultValidationError(f"Vault not found at {expanded_path}")
        if not os.path.isdir(expanded_path):
            raise VaultValidationError(f"Path is not a directory: {expanded_path}")
        return expanded_path

    def create_backup(self, encrypt: bool = False, password: Optional[str] = None) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"obsidian_backup_{timestamp}.tar.gz"

            with tempfile.TemporaryDirectory() as tmpdir:
                backup_path = os.path.join(tmpdir, backup_name)

                try:
                    with tarfile.open(backup_path, "w:gz") as tar:
                        tar.add(self.vault_path, arcname=os.path.basename(self.vault_path))
                except (tarfile.TarError, OSError) as e:
                    raise ArchiveError(f"Archive creation failed: {str(e)}")

                if encrypt:
                    if not password:
                        raise EncryptionError("Encryption password required")
                    try:
                        crypto = CryptoVault(password)
                        encrypted_path = backup_path + ".enc"
                        crypto.encrypt_file(backup_path, encrypted_path)
                        backup_path = encrypted_path
                    except Exception as e:
                        raise EncryptionError(f"Encryption failed: {str(e)}")

                final_path = os.path.join(os.getcwd(), os.path.basename(backup_path))
                os.replace(backup_path, final_path)

            return final_path

        except Exception as e:
            if isinstance(e, ObsidianBackupError):
                raise
            raise ArchiveError(f"Unexpected backup error: {str(e)}")