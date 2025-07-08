import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from obsidian_backuper.cli import main, get_env_var
from obsidian_backuper.exceptions import VaultValidationError, EncryptionError, DecryptionError
from obsidian_backuper.crypto import CryptoVault


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, "test_vault")
        os.makedirs(self.vault_dir)
        
        with open(os.path.join(self.vault_dir, "test_note.md"), "w") as f:
            f.write("# Test Note")
        
        self.encrypted_file = os.path.join(self.test_dir, "test.enc")
        crypto = CryptoVault("testpassword")
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        crypto.encrypt_file(test_file, self.encrypted_file)
        os.unlink(test_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_env_var(self):
        os.environ["TEST_VAR"] = "test_value"
        self.assertEqual(get_env_var("TEST_VAR"), "test_value")
        
        self.assertIsNone(get_env_var("NON_EXISTENT_VAR"))
        self.assertEqual(get_env_var("NON_EXISTENT_VAR", "default"), "default")

    @patch('obsidian_backuper.cli.argparse.ArgumentParser.parse_args')
    def test_cli_encrypt(self, mock_parse_args):
        mock_args = MagicMock()
        mock_args.vault = self.vault_dir
        mock_args.password = "testpassword"
        mock_args.encrypt = True
        mock_args.decrypt = False
        mock_parse_args.return_value = mock_args
        
        with patch('obsidian_backuper.cli.ObsidianBackuper') as mock_backuper:
            instance = mock_backuper.return_value
            instance.create_backup.return_value = "/path/to/backup.tar.gz.enc"
            
            main()
            
            mock_backuper.assert_called_once_with(vault_path=self.vault_dir)
            instance.create_backup.assert_called_once_with(encrypt=True, password="testpassword")

    @patch('obsidian_backuper.cli.argparse.ArgumentParser.parse_args')
    def test_cli_decrypt(self, mock_parse_args):
        mock_args = MagicMock()
        mock_args.vault = self.encrypted_file
        mock_args.password = "testpassword"
        mock_args.encrypt = False
        mock_args.decrypt = True
        mock_parse_args.return_value = mock_args
        
        with patch('obsidian_backuper.cli.ObsidianDecryptor') as mock_decryptor:
            instance = mock_decryptor.return_value
            instance.decrypt.return_value = "/path/to/decrypted_file"
            
            main()
            
            mock_decryptor.assert_called_once_with(encrypted_file_path=self.encrypted_file)
            instance.decrypt.assert_called_once_with(password="testpassword")

    @patch('obsidian_backuper.cli.argparse.ArgumentParser.parse_args')
    def test_cli_errors(self, mock_parse_args):
        mock_args = MagicMock()
        mock_args.vault = "/nonexistent/path"
        mock_args.password = "testpassword"
        mock_args.encrypt = True
        mock_args.decrypt = False
        mock_parse_args.return_value = mock_args
        
        with self.assertRaises(SystemExit):
            main()