[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)
[![Coverage Status](https://coveralls.io/repos/github/NikitaMarakushev/obsidian_backuper/badge.svg?branch=develop)](https://coveralls.io/github/NikitaMarakushev/obsidian_backuper?branch=develop)


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
```pip install dist/obsidian_backuper-1.0.2-py3-none-any.whl```

### Cli run encrypt:
```obsidian-backup --vault ~/my_vault --encrypt --password "secret"```

### Cli run decrypt:
```obsidian-backup --vault ~/path_to_folder_with_vault --decrypt --password "secret"```

### Uninstall:
```pip uninstall obsidian_backuper```

Alternative:
1) Run to venv setup:
```bash setup_venv.sh```
2) Run to build:
```bash build_and_install.sh & source .venv/bin/activate```

exit venv: ```deactivate```

Uninstall packege: ```pip uninstall obsidian-backuper -y```

Run with tui: ```obsidian-backup --tui```

![img.png](media/img.png)
![img_1.png](media/img_1.png)
![img3.png](media/img3.png)