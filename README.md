![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Simple cli tool for obsidian vault backup

### Install
1. `git clone https://github.com/NikitaMarakushev/obsidian_backuper`
2. `pip install -e .`

### Set up
Создайте `.env` файл:
<br>```VAULT_PATH=/your_obsidian_vault_path``` 
<br>```BACKUP_DIR=/your_obsidian_backup_vault_path```

### Create undecrypted vault
```python -m obsidian_backuper.cli --vault ~/my_vault```

### Create encrypted vault
```python -m obsidian_backuper.cli --vault ~/my_vault --encrypt --password "secret"```

### Decrypt
```python -c "
from obsidian_backuper.crypto import CryptoVault
CryptoVault('secret').decrypt_file('backup.enc', 'decrypted.tar.gz', 'secret')
"
```
### Run tests:
```pytest tests/ -v```

### With code coverage
```pytest --cov=src/obsidian_backuper tests/```

### Generate htlm template
```pytest --cov=src/obsidian_backuper --cov-report=html```

### Install test dependencies:
```pip install -e .[test]```

### Install builder:
```pip install build```

### Run build:
```python -m build```

### Install:
```pip install dist/obsidian_backuper-1.0.0-py3-none-any.whl```

### Cli run:
```obsidian-backup --vault ~/my_vault --encrypt --password "secret"```
