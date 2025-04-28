import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis do ambiente
load_dotenv()
api_key = os.getenv("API_KEY")
file_name = os.getenv("FILE_NAME")
count = int(os.getenv("COUNT", 10))

def get_routing_region(server_id):
    server_id = server_id.lower()
    if server_id in ['br1', 'na1', 'la1', 'la2', 'oc1']:
        return 'americas'
    elif server_id in ['euw1', 'eune1', 'tr1', 'ru']:
        return 'europe'
    elif server_id in ['kr', 'jp1']:
        return 'asia'
    return 'americas'

# Carregar CSV
try:
    df = pd.read_csv(file_name)
except Exception as e:
    print(f"Erro ao carregar arquivo {file_name}: {e}")
    exit()

# Loop por jogador
matches_list = []
total = len(df)
print(f"🔍 Iniciando busca de {count} partidas para {total} jogadores...")

for i, row in df.iterrows():
    name = row['Name']
    tag = row['Tag']
    puuid = row['puuid']
    server_id = row['Server']

    routing_region = get_routing_region(server_id)

    match_url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "queue": 420,
        "start": 0,
        "count": count,
        "api_key": api_key
    }

    try:
        resp = requests.get(match_url, params=params, timeout=10)
        if resp.status_code == 200:
            match_ids = resp.json()
            for match_id in match_ids:
                matches_list.append((match_id, routing_region))
        elif resp.status_code == 429:
            print(f"⚠️ Rate limit excedido para {name}. Aguardando 2 minutos...")
            time.sleep(120)
            continue
        else:
            print(f"❌ Erro {resp.status_code} para {name} - {server_id}")
            continue
    except Exception as e:
        print(f"Erro em {name}: {e}")
        continue

    if (i + 1) % 10 == 0:
        print(f"✔️ Processados: {i + 1}/{total}")

# Salvar resultado
df_out = pd.DataFrame(matches_list, columns=["Game", "Region"])
out_path = f"games_with_regions_{Path(file_name).stem}.csv"
df_out.to_csv(out_path, index=False)
print(f"✅ Arquivo salvo como {out_path}")