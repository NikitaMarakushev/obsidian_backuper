import os
import shutil
import tarfile
import tempfile
import logging
from datetime import datetime
from typing import Optional
from .exceptions import (
    VaultValidationError,
    EncryptionError,
    ArchiveError,
    ObsidianBackupError,
    DecryptionError
)
from .crypto import CryptoVault

logger = logging.getLogger(__name__)

class ObsidianBackuper:
    def __init__(self, vault_path: str, require_directory: bool = True):
        self.vault_path = self._validate_vault_path(vault_path, require_directory)

    def _validate_vault_path(self, path: str, require_directory: bool = True) -> str:
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            raise VaultValidationError(f"Vault or backup file not found at {expanded_path}")
        if require_directory and not os.path.isdir(expanded_path):
            raise VaultValidationError(f"Path is not a directory: {expanded_path}")
        return expanded_path
    
    def _validate_backup_file(self, path: str) -> str:
        if not os.path.isfile(path):
            raise ArchiveError(f"Backup path is not a file: {path}")
        return path

    def create_backup(self, encrypt: bool = False, password: Optional[str] = None) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"obsidian_backup_{timestamp}.tar.gz"
            vault_dir = os.path.dirname(os.path.abspath(self.vault_path))
            final_path = os.path.join(vault_dir, backup_name)

            if os.path.exists(final_path):
                raise ArchiveError(f"Backup file already exists: {final_path}")

            logger.info(f"Starting backup for vault: {self.vault_path}")

            with tempfile.TemporaryDirectory(dir=vault_dir) as tmpdir:
                backup_path = os.path.join(tmpdir, backup_name)
                logger.debug(f"Using temp dir: {tmpdir}")

                try:
                    with tarfile.open(backup_path, "w:gz") as tar:
                        tar.add(self.vault_path, arcname=os.path.basename(self.vault_path))
                    logger.debug(f"Temporary archive created: {backup_path}")
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
                        final_path += ".enc"
                        logger.debug(f"File encrypted: {backup_path}")
                    except Exception as e:
                        raise EncryptionError(f"Encryption failed: {str(e)}")

                shutil.copy2(backup_path, final_path)
                logger.info(f"Backup successfully created at: {final_path}")

            return final_path

        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            if isinstance(e, ObsidianBackupError):
                raise
            raise ArchiveError(f"Unexpected backup error: {str(e)}")

    def decrypt_backup(self, output_dir: str = None, password: Optional[str] = None) -> str:
        if not os.path.exists(self.vault_path):
            raise ArchiveError(f"Backup file not found: {self.vault_path}")
        if not os.path.isfile(self.vault_path):
            raise ArchiveError(f"Path is not a file: {self.vault_path}")
        if not password:
            raise EncryptionError("Password required for decryption")

        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(self.vault_path))

        decrypted_name = os.path.basename(self.vault_path).replace('.enc', '')
        temp_path = os.path.join(output_dir, f"tmp_{decrypted_name}")
        final_path = os.path.join(output_dir, decrypted_name)

        if not password:
            raise EncryptionError("Password required for decryption")

        crypto = CryptoVault(password)
        crypto.decrypt_file(self.vault_path, temp_path)
        logger.debug(f"File decrypted to temporary: {temp_path}")

        shutil.move(temp_path, final_path)
        logger.info(f"Backup decrypted to: {final_path}")
        return final_path