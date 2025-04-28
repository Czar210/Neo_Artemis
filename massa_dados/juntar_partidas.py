import os
import pandas as pd

# Caminho da pasta onde estão os arquivos
csv_dir = r"C:\Users\cesar\Desktop\trabalhos puc\Trabalho Engenharia Social LoL\Código\csv_partidas"

# Listar todos os arquivos válidos
arquivos = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.startswith("games_with_regions_") and f.endswith(".csv")]

print(f"🔍 {len(arquivos)} arquivos encontrados para junção.")

# Carregar e concatenar todos os arquivos
dfs = [pd.read_csv(f) for f in arquivos]
df_final = pd.concat(dfs, ignore_index=True)

# Salvar o resultado
saida = os.path.join(csv_dir, "games_with_regions_final.csv")
df_final.to_csv(saida, index=False)

print(f"✅ Arquivo final salvo em: {saida}")
