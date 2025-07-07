import unittest
import os
import tempfile
import shutil
import tarfile
from obsidian_backuper.core import ObsidianBackuper
from obsidian_backuper.exceptions import VaultValidationError, ArchiveError, EncryptionError
from obsidian_backuper.crypto import CryptoVault

class TestObsidianBackuper(unittest.TestCase):
    def setUp(self):
        # Create a test vault structure
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, "test_vault")
        os.makedirs(self.vault_dir)
        
        # Create some test files in the vault
        with open(os.path.join(self.vault_dir, "test_note.md"), "w") as f:
            f.write("# Test Note\n\nThis is a test note.")
        
        os.makedirs(os.path.join(self.vault_dir, "subdir"))
        with open(os.path.join(self.vault_dir, "subdir", "another_note.md"), "w") as f:
            f.write("# Another Note\n\nMore test content.")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_validate_vault_path(self):
        backuper = ObsidianBackuper(self.vault_dir)
        self.assertEqual(backuper.vault_path, self.vault_dir)
        
        with self.assertRaises(VaultValidationError):
            ObsidianBackuper(os.path.join(self.test_dir, "nonexistent"))
            
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test")
        with self.assertRaises(VaultValidationError):
            ObsidianBackuper(test_file)
        os.unlink(test_file)
        
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test")
        try:
            backuper = ObsidianBackuper(test_file, require_directory=False)
            self.assertEqual(backuper.vault_path, test_file)
        finally:
            os.unlink(test_file)

    def test_create_backup_unencrypted(self):
        backuper = ObsidianBackuper(self.vault_dir)
        backup_path = backuper.create_backup(encrypt=False)
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith(".tar.gz"))
        
        # Verify tar contents
        with tarfile.open(backup_path, "r:gz") as tar:
            members = tar.getmembers()
            self.assertTrue(any(m.name == "test_vault/test_note.md" for m in members))
            self.assertTrue(any(m.name == "test_vault/subdir/another_note.md" for m in members))
        
        os.unlink(backup_path)

    def test_create_backup_encrypted(self):
        password = "testpassword123"
        backuper = ObsidianBackuper(self.vault_dir)
        backup_path = backuper.create_backup(encrypt=True, password=password)
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith(".tar.gz.enc"))
        
        # Verify we can decrypt it
        crypto = CryptoVault(password)
        decrypted_path = backup_path[:-4]  # remove .enc
        crypto.decrypt_file(backup_path, decrypted_path)
        
        with tarfile.open(decrypted_path, "r:gz") as tar:
            members = tar.getmembers()
            self.assertTrue(any(m.name == "test_vault/test_note.md" for m in members))
        
        os.unlink(backup_path)
        os.unlink(decrypted_path)

    def test_create_backup_encrypted_no_password(self):
        backuper = ObsidianBackuper(self.vault_dir)
        with self.assertRaises(EncryptionError):
            backuper.create_backup(encrypt=True, password=None)

    def test_decrypt_backup(self):
        password = "testpassword123"
        
        backuper = ObsidianBackuper(self.vault_dir)
        encrypted_path = backuper.create_backup(encrypt=True, password=password)
        
        self.assertTrue(os.path.exists(encrypted_path))
        
        file_backuper = ObsidianBackuper(encrypted_path)
        decrypted_path = file_backuper.decrypt_backup(password=password)
    
        self.assertTrue(os.path.exists(decrypted_path))
        self.assertTrue(decrypted_path.endswith(".tar.gz"))
        
        os.unlink(encrypted_path)
        os.unlink(decrypted_path)

    def test_decrypt_backup_wrong_password(self):
        password = "testpassword123"
        wrong_password = "wrongpassword"
        
        backuper = ObsidianBackuper(self.vault_dir)
        encrypted_path = backuper.create_backup(encrypt=True, password=password)
        
        file_backuper = ObsidianBackuper(encrypted_path, require_directory=False)
        with self.assertRaises(EncryptionError):
            file_backuper.decrypt_backup(password=wrong_password)
        
        os.unlink(encrypted_path)