![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Simple cli tool for obsidian vault backup

### Install
1. `git clone https://github.com/NikitaMarakushev/obsidian_backuper`

### Set up your .env file

### Run tests:
```pytest tests/ -v```

### With code coverage
```pytest --cov=src/obsidian_backuper tests/```

### Generate htlm template
```pytest --cov=src/obsidian_backuper --cov-report=html```

### Create venv
```python3 -m venv .venv```

### Link venv
```source .venv/bin/activate```

### Install test dependencies:
```pip install -e .[test]```

### Install builder:
```pip install build```

### Run build:
```python -m build```

### Install:
```pip install dist/obsidian_backuper-1.0.0-py3-none-any.whl```

### Cli run encrypt:
```obsidian-backup --vault ~/my_vault --encrypt --password "secret"```

### Cli run decrypt:

### Uninstall:
```pip uninstall obsidian_backup```