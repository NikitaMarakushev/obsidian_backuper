import unittest
import os
import tempfile
from obsidian_backuper.crypto import CryptoVault
from obsidian_backuper.exceptions import EncryptionError

class TestCryptoVault(unittest.TestCase):
    def setUp(self):
        self.password = "securepassword123"
        self.test_data = b"Test data for encryption"
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.write(self.test_data)
        self.test_file.close()
        self.encrypted_file = tempfile.NamedTemporaryFile(delete=False).name
        self.decrypted_file = tempfile.NamedTemporaryFile(delete=False).name

    def tearDown(self):
        for f in [self.test_file.name, self.encrypted_file, self.decrypted_file]:
            if os.path.exists(f):
                os.unlink(f)

    def test_init_with_empty_password(self):
        with self.assertRaises(EncryptionError):
            CryptoVault("")

    def test_key_derivation(self):
        crypto = CryptoVault(self.password)
        self.assertEqual(len(crypto.key), 44)  # Fernet key is 32 bytes, base64 encoded

    def test_encrypt_decrypt_file(self):
        crypto = CryptoVault(self.password)
        
        # Encrypt
        crypto.encrypt_file(self.test_file.name, self.encrypted_file)
        self.assertTrue(os.path.exists(self.encrypted_file))
        self.assertGreater(os.path.getsize(self.encrypted_file), 0)
        
        # Decrypt
        crypto.decrypt_file(self.encrypted_file, self.decrypted_file)
        self.assertTrue(os.path.exists(self.decrypted_file))
        
        with open(self.decrypted_file, 'rb') as f:
            decrypted_data = f.read()
        
        self.assertEqual(decrypted_data, self.test_data)

    def test_decrypt_with_wrong_password(self):
        crypto = CryptoVault(self.password)
        crypto.encrypt_file(self.test_file.name, self.encrypted_file)
        
        wrong_crypto = CryptoVault("wrongpassword")
        with self.assertRaises(EncryptionError):
            wrong_crypto.decrypt_file(self.encrypted_file, self.decrypted_file)

    def test_decrypt_corrupted_file(self):
        crypto = CryptoVault(self.password)
        crypto.encrypt_file(self.test_file.name, self.encrypted_file)
        
        # Corrupt the file
        with open(self.encrypted_file, 'ab') as f:
            f.write(b"corrupt")
            
        with self.assertRaises(EncryptionError):
            crypto.decrypt_file(self.encrypted_file, self.decrypted_file)