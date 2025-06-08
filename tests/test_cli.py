import pytest
from click.testing import CliRunner
from src.obsidian_backuper.cli import main
from unittest.mock import patch


class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch("obsidian_backuper.cli.ObsidianBackuper")
    def test_basic_cli_call(self, mock_backuper, runner):
        """Тест вызова CLI с минимальными параметрами"""
        result = runner.invoke(main, ["--vault", "/fake/path"])
        assert result.exit_code == 0
        mock_backuper.assert_called_once_with(vault_path="/fake/path", remote_url=None)

    @patch("obsidian_backuper.cli.ObsidianBackuper")
    def test_encryption_cli(self, mock_backuper, runner):
        """Тест CLI с шифрованием"""
        mock_instance = mock_backuper.return_value
        mock_instance.create_backup.return_value = "/backup/path.tar.gz"

        result = runner.invoke(main, [
            "--vault", "/fake/path",
            "--encrypt",
            "--password", "secret"
        ])

        assert result.exit_code == 0
        mock_instance.create_backup.assert_called_once_with(
            encrypt=True,
            password="secret"
        )

    @patch("obsidian_backuper.cli.dotenv.load_dotenv")
    def test_env_vars_loading(self, mock_load, runner):
        """Проверка загрузки переменных окружения"""
        with runner.isolated_filesystem():
            with open(".env", "w") as f:
                f.write("VAULT_PATH=/env/path\nREMOTE_URL=git@env.com/repo.git")

            with patch("obsidian_backuper.cli.ObsidianBackuper") as mock_backuper:
                runner.invoke(main)
                mock_backuper.assert_called_once_with(
                    vault_path="/env/path",
                    remote_url="git@env.com/repo.git"
                )
                mock_load.assert_called_once()