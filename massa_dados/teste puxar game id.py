import requests
import time

# ==========================
# CONFIGURAÇÕES DE TESTE
# ==========================
api_key = "RGAPI-41c23279-637e-4820-99ce-af5011dffe8d"
summoner_name = "Zaras"
tag_line = "0210"

# === Funções auxiliares ===
def get_routing_region(server_id):
    if server_id in ['br1', 'na1', 'la1', 'la2', 'oc1']:
        return 'americas'
    elif server_id in ['euw1', 'eune1', 'tr1', 'ru']:
        return 'europe'
    elif server_id in ['kr', 'jp1']:
        return 'asia'
    return 'americas'

def detect_server_from_puuid(puuid, api_key):
    servers_to_try = ['br1', 'na1', 'euw1', 'eune1', 'lan', 'las', 'tr1', 'ru', 'kr', 'jp1', 'oc1', 'la1', 'la2']
    for server in servers_to_try:
        url = f"https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
        r = requests.get(url)
        if r.status_code == 200:
            print(f"✅ Servidor detectado: {server}")
            return server
    print("❌ Nenhum servidor conhecido respondeu com sucesso.")
    return None

# === Etapa 1: Buscar PUUID pela Riot ID ===
print(f"🔍 Buscando PUUID para {summoner_name}#{tag_line}")
account_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}?api_key={api_key}"

resp = requests.get(account_url)
if resp.status_code != 200:
    print(f"❌ Erro ao buscar PUUID: {resp.status_code}")
    try:
        print(resp.json())
    except:
        pass
    exit()

p_info = resp.json()
puuid = p_info["puuid"]
print(f"✅ PUUID encontrado: {puuid}")

# === Etapa 2: Descobrir servidor correto ===
server_id = detect_server_from_puuid(puuid, api_key)
if server_id is None:
    print("❌ Não foi possível determinar o servidor.")
    exit()

routing_region = get_routing_region(server_id)

# === Etapa 3: Buscar partidas ===
match_url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count=10&api_key={api_key}"

print(f"📥 Buscando partidas com rota: {routing_region}")
resp = requests.get(match_url)
if resp.status_code == 200:
    matches = resp.json()
    print(f"✅ Partidas encontradas: {len(matches)}")
    print(matches)
else:
    print(f"❌ Erro ao buscar partidas: {resp.status_code}")
    try:
        print(resp.json())
    except:
        pass