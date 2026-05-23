import os, shutil
from datetime import datetime


def backup_banco(db_path: str, backups_dir: str) -> str:
    os.makedirs(backups_dir, exist_ok=True)
    nome = f"pizzaria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = os.path.join(backups_dir, nome)
    if os.path.exists(db_path):
        shutil.copy2(db_path, destino)
    return destino
