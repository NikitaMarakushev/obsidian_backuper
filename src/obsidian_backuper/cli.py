import argparse
import os
import dotenv
import logging
from typing import Optional
from .core import ObsidianBackuper
from .exceptions import (
    ObsidianBackupError,
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
    value = os.getenv(name, default)
    if value is None:
        logging.warning(f"Environment variable {name} not set")
    return value

def main():
    setup_logging()
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to vault directory (for encrypt) or to encrypted archive (for decrypt)")
    parser.add_argument("--password", required=True, help="Encryption/decryption password")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encrypt", action="store_true", help="Create and encrypt backup")
    group.add_argument("--decrypt", action="store_true", help="Decrypt backup archive")

    args = parser.parse_args()

    try:
        if args.encrypt:
            if not os.path.isdir(os.path.expanduser(args.vault)):
                logging.error(f"Vault path must be a directory for encryption: {args.vault}")
                exit(1)

            backuper = ObsidianBackuper(vault_path=args.vault)
            backup_path = backuper.create_backup(
                encrypt=True,
                password=args.password
            )
            logging.info(f"Encrypted backup created at: {backup_path}")

        elif args.decrypt:
            decryptor = ObsidianDecryptor(encrypted_file_path=args.vault)
            decrypted_path = decryptor.decrypt(password=args.password)
            logging.info(f"File decrypted to: {decrypted_path}")

    except VaultValidationError as e:
        logging.error(f"Vault error: {str(e)}")
        exit(1)
    except EncryptionError as e:
        logging.error(f"Encryption error: {str(e)}")
        exit(1)
    except DecryptionError as e:
        logging.error(f"Decryption error: {str(e)}")
        exit(1)
    except ObsidianBackupError as e:
        logging.error(f"Backup error: {str(e)}")
        exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()
