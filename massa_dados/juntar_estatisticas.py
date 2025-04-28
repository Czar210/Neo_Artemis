import os
import pandas as pd

# Caminho da pasta onde estão os CSVs dos junglers
csv_dir = r"C:\Users\cesar\Desktop\trabalhos puc\Trabalho Engenharia Social LoL\Código\csv_estatisticas"

# Listar todos os arquivos que comecem com dados_junglers_part_
arquivos = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.startswith("dados_junglers_part_") and f.endswith(".csv")]

print(f"🔍 Encontrados {len(arquivos)} arquivos para junção.")

# Carregar todos os CSVs
dfs = [pd.read_csv(f) for f in arquivos]
df_final = pd.concat(dfs, ignore_index=True)

# Salvar o resultado final
saida = os.path.join(csv_dir, "dados_junglers_final.csv")
df_final.to_csv(saida, index=False)

print(f"✅ Arquivo final salvo em: {saida}")
