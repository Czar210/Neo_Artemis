import requests
from keys import API_KEYS

# Exemplo de invocação que funcionou no log
summoner_name = "Zaras"
tag = "0210"  # substitua se necessário
region = "americas"  # para Ziko (euw), o servidor correto para essa rota da Riot API é 'europe'

# Endpoint de teste (Account-V1)
def test_key(key):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}?api_key={key}"
    response = requests.get(url)
    if response.status_code == 200:
        return "✅ Funciona"
    else:
        try:
            return f"❌ {response.status_code} - {response.json().get('status', {}).get('message', 'Erro')}"
        except:
            return f"❌ {response.status_code} - Erro desconhecido"

# Rodar o teste
for i, key in enumerate(API_KEYS, 1):
    resultado = test_key(key)
    print(f"Chave {i}: {resultado}")
