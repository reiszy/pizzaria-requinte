import os
import pandas as pd


def exportar_xlsx(rows, columns, filename, exports_dir):
    os.makedirs(exports_dir, exist_ok=True)
    df = pd.DataFrame(rows, columns=columns)
    caminho = os.path.join(exports_dir, filename)
    df.to_excel(caminho, index=False)
    return caminho


def exportar_csv(rows, columns, filename, exports_dir):
    os.makedirs(exports_dir, exist_ok=True)
    df = pd.DataFrame(rows, columns=columns)
    caminho = os.path.join(exports_dir, filename)
    df.to_csv(caminho, index=False, sep=";", encoding="utf-8-sig")
    return caminho
