import os
import tarfile
import tempfile
from datetime import datetime
from git import Repo, InvalidGitRepositoryError, GitCommandError
from typing import Optional
from .exceptions import (
    GitOperationError,
    VaultValidationError,
    EncryptionError,
    ArchiveError, ObsidianBackupError
)
from .crypto import CryptoVault


class ObsidianBackuper:
    def __init__(self, vault_path: str, remote_url: Optional[str] = None):
        self.vault_path = self._validate_vault_path(vault_path)
        self.remote_url = remote_url
        self.repo = self._validate_repo()

    def _validate_vault_path(self, path: str) -> str:
        """Проверка существования vault"""
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            raise VaultValidationError(f"Vault not found at {expanded_path}")
        if not os.path.isdir(expanded_path):
            raise VaultValidationError(f"Path is not a directory: {expanded_path}")
        return expanded_path

    def _validate_repo(self) -> Repo:
        """Валидация Git-репозитория с детализированными ошибками"""
        try:
            repo = Repo(self.vault_path)
            if repo.bare:
                raise GitOperationError("Repository is bare")
            return repo
        except InvalidGitRepositoryError as e:
            raise GitOperationError(
                f"Path is not a Git repository: {self.vault_path}",
                git_error=e
            )
        except Exception as e:
            raise GitOperationError("Unexpected Git error", git_error=e)

    def create_backup(self, encrypt: bool = False, password: Optional[str] = None) -> str:
        """Создание архива с обработкой всех ошибок"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"obsidian_backup_{timestamp}.tar.gz"

            with tempfile.TemporaryDirectory() as tmpdir:
                backup_path = os.path.join(tmpdir, backup_name)

                # Архивация
                try:
                    with tarfile.open(backup_path, "w:gz") as tar:
                        tar.add(self.vault_path, arcname=os.path.basename(self.vault_path))
                except (tarfile.TarError, OSError) as e:
                    raise ArchiveError(f"Archive creation failed: {str(e)}")

                # Шифрование
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

                # Перенос файла
                final_path = os.path.join(os.getcwd(), os.path.basename(backup_path))
                os.replace(backup_path, final_path)

            return final_path

        except Exception as e:
            if isinstance(e, ObsidianBackupError):
                raise
            raise ArchiveError(f"Unexpected backup error: {str(e)}")

    def push_to_remote(self):
        """Отправка изменений с обработкой Git-ошибок"""
        if not self.remote_url:
            raise GitOperationError("Remote URL not configured")

        try:
            origin = self.repo.remote(name="origin")
            origin.push(all=True)
        except GitCommandError as e:
            raise GitOperationError("Git push failed", git_error=e)