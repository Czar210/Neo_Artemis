import os
import subprocess
import pandas as pd
import math
from keys import API_KEYS

base_dir = os.path.dirname(__file__)
input_path = os.path.join(base_dir, "..", "dados e afins", "summoners_data_savino.csv")

df = pd.read_csv(input_path)
num_rows = len(df)
n_processes = len(API_KEYS)
batch_size = math.ceil(num_rows / n_processes)

# Criar pasta para dividir os arquivos
output_dir = os.path.join(base_dir, "csv_puuid")
os.makedirs(output_dir, exist_ok=True)

file_names = []
for i in range(n_processes):
    start_idx = i * batch_size
    end_idx = min(start_idx + batch_size, num_rows)
    sub_df = df.iloc[start_idx:end_idx]
    file_name = os.path.join(output_dir, f"summoners_data_part_{i+1}.csv")
    sub_df.to_csv(file_name, index=False)
    file_names.append(file_name)

# Caminho do processo filho
child_path = os.path.join(base_dir, "processo_filho_puuid.py")

# Iniciar subprocessos em janelas CMD com KEY_ID
for i, key in enumerate(API_KEYS):
    env = os.environ.copy()
    env["API_KEY"] = key
    env["FILE_NAME"] = file_names[i]
    env["KEY_ID"] = str(i + 1)

    subprocess.Popen(
        f'start cmd /k python "{child_path}"',
        env=env,
        shell=True
    )

print("Processos iniciados para coleta de PUUID com KEY_ID correspondente.")