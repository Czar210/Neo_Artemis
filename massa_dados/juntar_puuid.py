import os
import pandas as pd

# Caminho da pasta contendo os arquivos CSV
base_path = r"C:\Users\cesar\Desktop\trabalhos puc\Trabalho Engenharia Social LoL\Código"
csv_folder = os.path.join(base_path, "csv_puuid")

# Listar arquivos .csv dentro da pasta
csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.endswith(".csv")]

print(f"🔎 Encontrados {len(csv_files)} arquivos para junção.")

# Carregar e concatenar
dfs = [pd.read_csv(f) for f in csv_files]
df_final = pd.concat(dfs, ignore_index=True)

# Salvar o resultado
output_path = os.path.join(base_path, "summoners_data_final.csv")
df_final.to_csv(output_path, index=False)

print(f"✅ Arquivo final salvo em: {output_path}")
