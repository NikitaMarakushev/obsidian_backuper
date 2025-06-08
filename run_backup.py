import os
from datetime import datetime
import zipfile
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv(".env")

vault_path  = os.getenv('VAULT_PATH')
backup_dir = os.getenv('BACKUP_DIR')

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

def backup_obsidian_vault():
    now = datetime.now()
    timestamp = now.strftime(DATETIME_FORMAT)
    backup_filename = f'obsidian_backup_{timestamp}.zip'
    backup_path = os.path.join(backup_dir, backup_filename)

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for folder_name, subfolders, filenames in os.walk(vault_path):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                archive_name = os.path.relpath(file_path, vault_path)
                backup_zip.write(file_path, archive_name)
    print(f'New backup is created at: {backup_path}')

def encrypt_file(key: bytes, input_path: Path, output_path: Path):
    fernet = Fernet(key)
    with open(input_path, 'rb') as f:
        encrypted = fernet.encrypt(f.read())
    output_path.write_bytes(encrypted)

def validate_vault_path(path: Path) -> bool:
    return path.exists() and (path / '.obsidian').is_dir()

if __name__ == '__main__':
    backup_obsidian_vault()