import os
import pytest
from pathlib import Path
from src.obsidian_backuper.crypto import CryptoVault
from src.obsidian_backuper.exceptions import EncryptionError

class TestCryptoVault:
    @pytest.fixture
    def test_data(self, tmp_path):
        data_file = tmp_path / "data.txt"
        data_file.write_text("Confidential: 12345")
        return data_file

    def test_encrypt_decrypt_cycle(self, test_data, tmp_path):
        """Полный цикл шифрования-дешифрования"""
        crypto = CryptoVault("strong-p@ss")
        encrypted = tmp_path / "encrypted.enc"
        decrypted = tmp_path / "decrypted.txt"

        # Шифрование
        crypto.encrypt_file(str(test_data), str(encrypted))
        assert os.path.exists(encrypted)
        assert os.path.getsize(encrypted) > 0

        # Дешифрование
        crypto.decrypt_file(str(encrypted), str(decrypted), "strong-p@ss")
        assert decrypted.read_text() == "Confidential: 12345"

    def test_wrong_password_fails(self, test_data, tmp_path):
        """Неверный пароль должен вызывать ошибку"""
        crypto = CryptoVault("right-password")
        encrypted = tmp_path / "test.enc"
        crypto.encrypt_file(str(test_data), str(encrypted))

        with pytest.raises(EncryptionError, match="Invalid password"):
            crypto.decrypt_file(str(encrypted), "output.txt", "wrong-password")

    def test_corrupted_file_handling(self, tmp_path):
        """Повреждённый файл должен вызывать ошибку"""
        corrupt_file = tmp_path / "corrupt.enc"
        corrupt_file.write_bytes(b"invalid" + os.urandom(32))

        with pytest.raises(EncryptionError, match="corrupted"):
            CryptoVault("any").decrypt_file(str(corrupt_file), "out.txt", "any")

    def test_empty_file_protection(self, tmp_path):
        """Пустые файлы должны обрабатываться корректно"""
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()

        crypto = CryptoVault("pass")
        with pytest.raises(EncryptionError, match="empty"):
            crypto.encrypt_file(str(empty_file), "out.enc")