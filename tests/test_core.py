import os

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from src.obsidian_backuper.core import ObsidianBackuper
from src.obsidian_backuper.exceptions import *


class TestObsidianBackuper:
    @pytest.fixture
    def mock_repo(self):
        repo = Mock(spec=Repo)
        repo.remote.return_value.push.return_value = True
        return repo

    def test_valid_vault_initialization(self, tmp_path):
        """Инициализация с существующим vault"""
        vault_dir = tmp_path / "vault"
        vault_dir.mkdir()
        (vault_dir / ".git").mkdir()  # Делаем вид, что это git repo

        backuper = ObsidianBackuper(str(vault_dir))
        assert isinstance(backuper.repo, Repo)

    @pytest.mark.parametrize("path", [
        "/nonexistent/path",
        str(Path(__file__).absolute())  # Указываем файл вместо директории
    ])
    def test_invalid_vault_paths(self, path):
        """Проверка невалидных путей"""
        with pytest.raises(VaultValidationError):
            ObsidianBackuper(path)

    @patch("obsidian_backuper.core.Repo")
    def test_git_errors_handling(self, mock_repo):
        """Обработка различных ошибок Git"""
        # Случай 1: Не Git репозиторий
        mock_repo.side_effect = InvalidGitRepositoryError()
        with pytest.raises(GitOperationError, match="not a Git repository"):
            ObsidianBackuper("/valid/path")

        # Случай 2: Ошибка push
        mock_repo.reset_mock()
        mock_repo.return_value.remote.return_value.push.side_effect = Exception("Push failed")
        backuper = ObsidianBackuper("/valid/path", remote_url="git@example.com/repo.git")
        with pytest.raises(GitOperationError, match="Push failed"):
            backuper.push_to_remote()

    @patch("obsidian_backuper.core.tarfile.open")
    def test_backup_creation_errors(self, mock_tarfile, tmp_path):
        """Ошибки при создании архива"""
        vault_dir = tmp_path / "vault"
        vault_dir.mkdir()

        # Случай 1: Ошибка создания tar
        mock_tarfile.side_effect = Exception("Tar error")
        backuper = ObsidianBackuper(str(vault_dir))
        with pytest.raises(ArchiveError, match="Tar error"):
            backuper.create_backup()

        # Случай 2: Успешное создание с шифрованием
        mock_tarfile.reset_mock()
        with patch("obsidian_backuper.core.CryptoVault") as mock_crypto:
            backuper.create_backup(encrypt=True, password="secret")
            assert mock_crypto.called

    def test_real_backup_flow(self, tmp_path):
        """Полный тест рабочего потока без моков"""
        # 1. Подготовка тестового vault
        vault_dir = tmp_path / "test_vault"
        vault_dir.mkdir()
        (vault_dir / "test_note.md").write_text("# Important Note")

        # 2. Инициализация Git
        repo = Repo.init(vault_dir)
        repo.index.add(["test_note.md"])
        repo.index.commit("Initial commit")

        # 3. Создание бэкапа
        backuper = ObsidianBackuper(str(vault_dir))
        backup_path = backuper.create_backup()

        assert Path(backup_path).exists()
        assert backup_path.endswith(".tar.gz")
        assert os.path.getsize(backup_path) > 0