# call_api_riot.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('RIOT_API_KEY')

def get_routing_region(server_id):
    if server_id in ['br1', 'na1', 'la1', 'la2', 'oc1']:
        return 'americas'
    elif server_id in ['euw1', 'eune1', 'tr1', 'ru']:
        return 'europe'
    elif server_id in ['kr', 'jp1']:
        return 'asia'
    return 'americas'

def detect_server_from_puuid(puuid):
    servers_to_try = ['br1', 'na1', 'euw1', 'eune1', 'lan', 'las', 'tr1', 'ru', 'kr', 'jp1', 'oc1', 'la1', 'la2']
    for server in servers_to_try:
        url = f"https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={API_KEY}"
        r = requests.get(url)
        if r.status_code == 200:
            print(f"✅ Servidor detectado: {server}")
            return server
    print("❌ Nenhum servidor conhecido respondeu com sucesso.")
    return None

def buscar_puuid(nome, tag, _):
    if not API_KEY:
        raise Exception("API Key não encontrada.")
    
    print(f"🔍 Buscando PUUID para {nome}#{tag}")
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nome}/{tag}?api_key={API_KEY}"

    while True:
        resp = requests.get(url)

        if resp.status_code == 200:
            puuid = resp.json()['puuid']
            print(f"✅ PUUID encontrado: {puuid}")
            return puuid

        elif resp.status_code == 429:
            print("⚠️ Rate limit excedido ao buscar PUUID! Aguardando 2 minutos...")
            time.sleep(120)
            continue

        elif resp.status_code == 404:
            raise Exception(f"Jogador {nome}#{tag} não encontrado.")

        else:
            raise Exception(f"Erro inesperado ({resp.status_code}): {resp.text}")


def buscar_partidas(puuid, plataforma, quantidade=30):
    if not API_KEY:
        raise Exception("API Key não encontrada.")

    server_id = detect_server_from_puuid(puuid)
    if server_id is None:
        raise Exception("Servidor não encontrado.")

    routing_region = get_routing_region(server_id)

    print(f"📥 Buscando partidas na região: {routing_region}")
    match_url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count={quantidade}&api_key={API_KEY}"

    while True:
        resp = requests.get(match_url)

        if resp.status_code == 200:
            matches = resp.json()
            print(f"✅ {len(matches)} partidas encontradas.")
            return matches

        elif resp.status_code == 429:
            print("⚠️ Rate limit excedido ao buscar partidas! Aguardando 2 minutos...")
            time.sleep(120)
            continue

        else:
            raise Exception(f"Erro inesperado ao buscar partidas ({resp.status_code}): {resp.text}")



import time  # Não esquecer de importar!

def buscar_detalhes_partida(match_id, plataforma):
    if not API_KEY:
        raise Exception("API Key não encontrada.")

    routing_region = get_routing_region(plataforma)

    url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"

    while True:
        resp = requests.get(url)

        if resp.status_code == 200:
            return resp.json()

        elif resp.status_code == 429:
            print("⚠️ Rate limit excedido! Aguardando 2 minutos...")
            time.sleep(120)
            continue  # Tenta novamente após dormir

        else:
            raise Exception(f"Erro ao buscar detalhes da partida: {resp.text}")


def extrair_estatisticas(partida_json, puuid):
    participants = partida_json['info']['participants']
    for p in participants:
        if p['puuid'] == puuid:
            # Verificar se o jogador tinha Smite (summonerSpellId 11)
            if p['summoner1Id'] != 11 and p['summoner2Id'] != 11:
                return None  # Ignorar partidas sem Smite

            return {
                'championName': p['championName'],
                'win': int(p['win']),
                'kills': p['kills'],
                'soloKills': p.get('soloKills', 0),
                'damagePerMinute': p.get('challenges', {}).get('damagePerMinute', 0),
                'killParticipation': p.get('challenges', {}).get('killParticipation', 0),
                'killsNearEnemyTurret': p.get('challenges', {}).get('killsNearEnemyTurret', 0),
                'killsOnOtherLanesEarlyJungleAsLaner': p.get('challenges', {}).get('killsOnOtherLanesEarlyJungleAsLaner', 0),
                'killsUnderOwnTurret': p.get('challenges', {}).get('killsUnderOwnTurret', 0),
                'quadraKills': p['quadraKills'],
                'takedowns': p.get('challenges', {}).get('takedowns', 0),
                'visionScore': p['visionScore'],
                'wardsPlaced': p.get('wardsPlaced', 0),
                'wardsKilled': p.get('wardsKilled', 0),
                'controlWardsPlaced': p.get('controlWardsPlaced', 0),
                'objectivesStolen': p.get('objectivesStolen', 0),
                'epicMonsterSteals': p.get('epicMonsterSteals', 0),
                'baronKills': p.get('baronKills', 0),
                'dragonTakedowns': p.get('challenges', {}).get('dragonTakedowns', 0),
                'riftHeraldTakedowns': p.get('challenges', {}).get('riftHeraldTakedowns', 0),
                'epicMonsterKillsNearEnemyJungler': p.get('challenges', {}).get('epicMonsterKillsNearEnemyJungler', 0),
                'epicMonsterKillsWithin30SecondsOfSpawn': p.get('challenges', {}).get('epicMonsterKillsWithin30SecondsOfSpawn', 0),
                'goldEarned': p['goldEarned'],
                'goldPerMinute': p.get('challenges', {}).get('goldPerMinute', 0),
                'champExperience': p['champExperience'],
                'jungleCsBefore10Minutes': p.get('challenges', {}).get('jungleCsBefore10Minutes', 0),
                'initialBuffCount': p.get('challenges', {}).get('initialBuffCount', 0),
                'initialCrabCount': p.get('challenges', {}).get('initialCrabCount', 0),
                'totalAllyJungleMinionsKilled': p.get('totalAllyJungleMinionsKilled', 0),
                'alliedJungleMonsterKills': p.get('challenges', {}).get('alliedJungleMonsterKills', 0),
                'totalEnemyJungleMinionsKilled': p.get('totalEnemyJungleMinionsKilled', 0),
                'enemyJungleMonsterKills': p.get('challenges', {}).get('enemyJungleMonsterKills', 0),
                'damageDealtToBuildings': p.get('damageDealtToBuildings', 0),
                'damageDealtToObjectives': p.get('damageDealtToObjectives', 0),
                'turretKills': p.get('turretKills', 0),
                'inhibitorKills': p.get('inhibitorKills', 0),
                'turretTakedowns': p.get('challenges', {}).get('turretTakedowns', 0),
                'teamRiftHeraldKills': p.get('teamRiftHeraldKills', 0),
                'teamBaronKills': p.get('teamBaronKills', 0),
                'deaths': p['deaths'],
                'totalDamageTaken': p['totalDamageTaken'],
                'longestTimeSpentLiving': p.get('longestTimeSpentLiving', 0),
                'survivedSingleDigitHpCount': p.get('challenges', {}).get('survivedSingleDigitHpCount', 0),
                'survivedThreeImmobilizesInFight': p.get('challenges', {}).get('survivedThreeImmobilizesInFight', 0),
                'kda': p.get('challenges', {}).get('kda', 0),
                'totalTimeCCDealt': p['totalTimeCCDealt'],
                'enemyChampionImmobilizations': p.get('enemyChampionImmobilizations', 0),
                'immobilizeAndKillWithAlly': p.get('challenges', {}).get('immobilizeAndKillWithAlly', 0),
                'knockEnemyIntoTeamAndKill': p.get('challenges', {}).get('knockEnemyIntoTeamAndKill', 0),
                'landSkillShotsEarlyGame': p.get('challenges', {}).get('landSkillShotsEarlyGame', 0),
                'earlyLaningPhaseGoldExpAdvantage': p.get('challenges', {}).get('earlyLaningPhaseGoldExpAdvantage', 0),
                'laningPhaseGoldExpAdvantage': p.get('challenges', {}).get('laningPhaseGoldExpAdvantage', 0),
                'takedownsBeforeJungleMinionSpawn': p.get('challenges', {}).get('takedownsBeforeJungleMinionSpawn', 0),
                'voidMonsterKill': p.get('challenges', {}).get('voidMonsterKill', 0),
                'totalDamageDealtToChampions': p.get('totalDamageDealtToChampions', 0)
            }
    return None

