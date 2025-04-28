import os
import subprocess
import time
import pandas as pd
import math
from keys import API_KEYS

base_dir = os.path.dirname(__file__)
input_path = os.path.join(base_dir, "..", "dados e afins", "summoners_data_final.csv")
output_dir = os.path.join(base_dir, "csv_partidas")
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)
file_names = []

# Dividir o CSV com base na coluna Key_ID
for i, key in enumerate(API_KEYS):
    key_id = str(i + 1)
    df_subset = df[df['Key_ID'].astype(str) == key_id]
    file_name = os.path.join(output_dir, f"summoners_data_part_{i+1}.csv")
    df_subset.to_csv(file_name, index=False)
    file_names.append(file_name)

# Caminho do processo filho
child_path = os.path.join(base_dir, "processo_filho_partidas.py")

# Iniciar subprocessos com janelas CMD separadas e COUNT = 30
for i, key in enumerate(API_KEYS):
    env = os.environ.copy()
    env["API_KEY"] = key
    env["FILE_NAME"] = file_names[i]
    env["COUNT"] = "50"

    subprocess.Popen(
        f'start cmd /k python "{child_path}"',
        env=env,
        shell=True
    )

print("Todos os processos de partidas foram iniciados com base no Key_ID.")