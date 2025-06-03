![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Simple cli tool for obsidian vault backup

Сopy the file ```.env.dist``` to ```.env``` and write the values for the variables, where

```VAULT_PATH=/your_obsidian_vault_path``` <br>
```BACKUP_DIR=/your_obsidian_backup_vault_path```

<b> python3 -m venv .venv</b>
<br><b>source .venv/bin/activate</b>
<br><b>pip install -r requirements.txt</b>

Run: <b>python3 run_backup.py</b>