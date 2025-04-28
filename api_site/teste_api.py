# teste_api.py

import requests
import time
import os
import sqlite3
from dotenv import load_dotenv

# ============================
# Configurações
# ============================
BASE_URL = "http://localhost:5000"
DB_NAME = "banco_jogadores.db"

SUMMONER_NAME = "FURIA Tatu"  # <- Muda conforme necessário
TAG_LINE = "10y"
PLATFORM = "br1"
QUANTIDADE_PARTIDAS = 40

# ============================
# Funções de Infraestrutura
# ============================

def checar_banco_dados():
    print("\n🛠️ Verificando Banco de Dados...")
    if not os.path.exists(DB_NAME):
        print(f"❌ Banco '{DB_NAME}' não encontrado!")
        return False

    print(f"✅ Banco '{DB_NAME}' encontrado.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    tabelas_esperadas = ['partidas_jogadores', 'scores_jogadores']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas_encontradas = [row[0] for row in cursor.fetchall()]

    sucesso = True
    for tabela in tabelas_esperadas:
        if tabela in tabelas_encontradas:
            print(f"✅ Tabela encontrada: {tabela}")
        else:
            print(f"❌ Tabela faltando: {tabela}")
            sucesso = False

    conn.close()
    return sucesso

def listar_partidas_salvas():
    print("\n📋 Listando partidas salvas no banco...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nickname, platform, championName, win FROM partidas_jogadores LIMIT 20;")
    partidas = cursor.fetchall()
    conn.close()

    if partidas:
        for partida in partidas:
            print(f"ID: {partida[0]}, Nickname: {partida[1]}, Plataforma: {partida[2]}, Campeão: {partida[3]}, Vitória: {partida[4]}")
    else:
        print("⚠️ Nenhuma partida encontrada no banco.")

def checar_bibliotecas():
    print("\n📦 Verificando bibliotecas essenciais...")
    try:
        import flask
        import pandas
        import numpy
        import dotenv
        print("✅ Bibliotecas essenciais instaladas.")
    except ImportError as e:
        print(f"❌ Biblioteca faltando: {e}")

def checar_api_key():
    print("\n🔑 Verificando API Key...")
    load_dotenv()
    api_key = os.getenv('RIOT_API_KEY')
    if api_key and len(api_key) > 10:
        print("✅ API Key carregada corretamente.")
        return api_key
    else:
        print("❌ API Key inválida ou não encontrada.")
        return None

# ============================
# Funções de Teste de API
# ============================

def testar_analisar_jogador(nome, tag, plataforma):
    print("\n[TESTE] 🔥 Testando /analisar_jogador...")
    payload = {
        "nome": nome,
        "tag": tag,
        "platform": plataforma,
        "quantidade": QUANTIDADE_PARTIDAS
    }
    try:
        response = requests.post(f"{BASE_URL}/analisar_jogador", json=payload)
        if response.status_code == 200:
            print("✅ Jogador analisado e partidas salvas com sucesso!")
            return True
        else:
            print(f"❌ Erro ao analisar jogador ({response.status_code}): {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def testar_scores(nome):
    print("\n[TESTE] 📈 Testando /scores...")
    try:
        response = requests.get(f"{BASE_URL}/scores", params={"nickname": nome})
        data = response.json()

        if response.status_code == 200 and isinstance(data, dict):
            print("✅ Scores calculados:")
            notas = []
            for key, value in data.items():
                print(f"- {key}: {value:.2f}")
                notas.append(value)

            if notas:
                media_scores = sum(notas) / len(notas)
                print(f"\n📊 Nota Média do Jogador: {media_scores:.2f}/10")

            return True
        else:
            print(f"❌ Erro ao calcular scores ({response.status_code}): {data}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def testar_recomendacoes(nome):
    print("\n[TESTE] 🧠 Testando /recomendar...")
    try:
        response = requests.get(f"{BASE_URL}/recomendar", params={"nickname": nome})
        data = response.json()

        if response.status_code == 200 and isinstance(data, list):
            if len(data) == 0:
                print("⚠️ Nenhuma recomendação encontrada.")
            else:
                print("✅ Recomendações obtidas:")
                similaridades = []
                for rec in data:
                    print(f"- {rec['campeao']}: Similaridade {rec['similaridade']}/10")
                    similaridades.append(rec['similaridade'])

                if similaridades:
                    media_similaridade = sum(similaridades) / len(similaridades)
                    print(f"\n📈 Média de Similaridade: {media_similaridade:.2f}/10")
            return True
        else:
            print(f"❌ Erro ao recomendar ({response.status_code}): {data}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

# ============================
# Execução Principal
# ============================

if __name__ == "__main__":
    print("\n===================================")
    print("INICIANDO TESTE COMPLETO API + BANCO")
    print("===================================")

    checar_bibliotecas()
    api_key = checar_api_key()
    if not api_key:
        exit()

    banco_ok = checar_banco_dados()
    if not banco_ok:
        print("⚠️ Banco de dados com problemas. Corrija antes de prosseguir.\n")
        exit()

    listar_partidas_salvas()

    sucesso_coleta = testar_analisar_jogador(SUMMONER_NAME, TAG_LINE, PLATFORM)

    if sucesso_coleta:
        time.sleep(2)
        sucesso_scores = testar_scores(SUMMONER_NAME)

        if sucesso_scores:
            time.sleep(1)
            testar_recomendacoes(SUMMONER_NAME)

    print("\n✅ [TESTE COMPLETO FINALIZADO] ✅")
