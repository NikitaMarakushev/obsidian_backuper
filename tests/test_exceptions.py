import unittest
from obsidian_backup.exceptions import (
    ObsidianBackupError,
    VaultValidationError,
    EncryptionError,
    ArchiveError,
    ConfigError,
    DecryptionError
)

class TestExceptions(unittest.TestCase):
    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(VaultValidationError, ObsidianBackupError))
        self.assertTrue(issubclass(EncryptionError, ObsidianBackupError))
        self.assertTrue(issubclass(ArchiveError, ObsidianBackupError))
        self.assertTrue(issubclass(ConfigError, ObsidianBackupError))
        self.assertTrue(issubclass(DecryptionError, ObsidianBackupError))

    def test_exception_messages(self):
        with self.assertRaises(VaultValidationError) as context:
            raise VaultValidationError("Test message")
        self.assertEqual(str(context.exception), "Test message")