class ObsidianBackupError(Exception):
    pass

class VaultValidationError(ObsidianBackupError):
    pass

class EncryptionError(ObsidianBackupError):
    pass

class ArchiveError(ObsidianBackupError):
    pass

class ConfigError(ObsidianBackupError):
    pass