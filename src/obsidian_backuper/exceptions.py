class ObsidianBackupError(Exception):
    """Базовое исключение для всех ошибок бэкапа"""
    pass

class GitOperationError(ObsidianBackupError):
    """Ошибки Git-операций"""
    def __init__(self, message: str, git_error: Exception = None):
        super().__init__(f"Git error: {message}. Details: {str(git_error) if git_error else 'N/A'}")
        self.git_error = git_error

class VaultValidationError(ObsidianBackupError):
    """Ошибки валидации vault"""
    pass

class EncryptionError(ObsidianBackupError):
    """Ошибки шифрования/дешифрования"""
    pass

class ArchiveError(ObsidianBackupError):
    """Ошибки работы с архивами"""
    pass

class ConfigError(ObsidianBackupError):
    """Ошибки конфигурации"""
    pass