import argparse
import os
import dotenv
import logging
from typing import Optional
from .core import ObsidianBackuper
from .exceptions import (
    ObsidianBackupError,
    GitOperationError,
    VaultValidationError,
    EncryptionError
)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('obsidian_backup.log'),
            logging.StreamHandler()
        ]
    )


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Безопасное получение переменных окружения"""
    value = os.getenv(name, default)
    if value is None:
        logging.warning(f"Environment variable {name} not set")
    return value


def main():
    setup_logging()
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=get_env_var("VAULT_PATH", "~/obsidian"))
    parser.add_argument("--remote", default=get_env_var("REMOTE_URL"))
    parser.add_argument("--encrypt", action="store_true")
    parser.add_argument("--password", default=get_env_var("BACKUP_PASSWORD"))

    args = parser.parse_args()

    try:
        backuper = ObsidianBackuper(
            vault_path=args.vault,
            remote_url=args.remote
        )

        backup_path = backuper.create_backup(
            encrypt=args.encrypt,
            password=args.password
        )
        logging.info(f"Backup created: {backup_path}")

        if backuper.remote_url:
            backuper.push_to_remote()
            logging.info("Changes pushed to remote repository")

    except VaultValidationError as e:
        logging.error(f"Vault error: {str(e)}")
        exit(1)
    except EncryptionError as e:
        logging.error(f"Encryption error: {str(e)}")
        exit(1)
    except GitOperationError as e:
        logging.error(f"Git error: {str(e)}")
        if e.git_error:
            logging.debug(f"Git details: {str(e.git_error)}")
        exit(1)
    except ObsidianBackupError as e:
        logging.error(f"Backup error: {str(e)}")
        exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()