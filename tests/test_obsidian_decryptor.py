import unittest
import os
import tempfile
from obsidian_backuper.obsidian_decryptor import ObsidianDecryptor
from obsidian_backuper.exceptions import ArchiveError, DecryptionError
from obsidian_backuper.crypto import CryptoVault


class TestObsidianDecryptor(unittest.TestCase):
    def setUp(self):
        self.password = "testpassword"
        self.test_data = b"Test data for decryption"
        
        self.encrypted_file = tempfile.NamedTemporaryFile(suffix='.enc', delete=False).name
        self.crypto = CryptoVault(self.password)
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.write(self.test_data)
        self.test_file.close()
        self.crypto.encrypt_file(self.test_file.name, self.encrypted_file)

    def tearDown(self):
        for f in [self.test_file.name, self.encrypted_file]:
            if os.path.exists(f):
                os.unlink(f)

    def test_validate_encrypted_file(self):
        decryptor = ObsidianDecryptor(self.encrypted_file)
        self.assertEqual(decryptor.encrypted_file_path, self.encrypted_file)
        
        with self.assertRaises(ArchiveError):
            ObsidianDecryptor("/nonexistent/file.enc")
            
        with self.assertRaises(ArchiveError):
            ObsidianDecryptor(os.path.dirname(self.encrypted_file))
            
        wrong_ext = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
        with self.assertRaises(ArchiveError):
            ObsidianDecryptor(wrong_ext)
        os.unlink(wrong_ext)

    def test_decrypt(self):
        decryptor = ObsidianDecryptor(self.encrypted_file)
        output_file = decryptor.decrypt(self.password)
        
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'rb') as f:
            content = f.read()
        self.assertEqual(content, self.test_data)
        os.unlink(output_file)

    def test_decrypt_with_wrong_password(self):
        decryptor = ObsidianDecryptor(self.encrypted_file)
        with self.assertRaises(DecryptionError):
            decryptor.decrypt("wrongpassword")

    def test_decrypt_with_output_dir(self):
        output_dir = tempfile.mkdtemp()
        decryptor = ObsidianDecryptor(self.encrypted_file)
        output_file = decryptor.decrypt(self.password, output_dir)
        
        self.assertTrue(os.path.exists(output_file))
        self.assertEqual(os.path.dirname(output_file), output_dir)
        
        with open(output_file, 'rb') as f:
            content = f.read()
        self.assertEqual(content, self.test_data)
        
        os.unlink(output_file)
        os.rmdir(output_dir)