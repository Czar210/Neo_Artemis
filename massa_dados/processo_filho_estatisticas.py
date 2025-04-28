import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api_key = os.getenv("API_KEY")
file_name = os.getenv("FILE_NAME")
key_id = os.getenv("KEY_ID", "1")

importante = [
    "championName", "riotIdGameName", "riotIdTagline", "summoner1Id", "summoner2Id"
]

not_challenges = [
    "deaths", "kills", "assists", "champExperience", "totalDamageDealt",
    "totalDamageDealtToChampions", "totalDamageTaken", "damageDealtToBuildings",
    "damageDealtToObjectives", "turretKills", "inhibitorKills", "visionScore",
    "wardsPlaced", "wardsKilled", "goldEarned", "goldSpent",
    "earlyLaningPhaseGoldExpAdvantage", "firstBloodAssist", "firstBloodKill",
    "gameEndedInEarlySurrender", "largestKillingSpree", "largestMultiKill",
    "longestTimeSpentLiving", "objectivesStolen", "totalAllyJungleMinionsKilled",
    "totalEnemyJungleMinionsKilled", "totalHealsOnTeammates", "totalTimeCCDealt",
    "totalTimeSpentDead", "quadraKills", "tripleKills", "doubleKills",
    "baronKills", "bountyLevel",
]

challenges = [
    "alliedJungleMonsterKills", "baronTakedowns", "buffsStolen", "controlWardsPlaced",
    "damagePerMinute", "dragonTakedowns", "earlyLaningPhaseGoldExpAdvantage",
    "enemyChampionImmobilizations", "enemyJungleMonsterKills", "epicMonsterKillsNearEnemyJungler",
    "epicMonsterKillsWithin30SecondsOfSpawn", "epicMonsterSteals", "gameLength", "goldPerMinute",
    "immobilizeAndKillWithAlly", "initialBuffCount", "initialCrabCount", "jungleCsBefore10Minutes",
    "junglerTakedownsNearDamagedEpicMonster", "kda", "killAfterHiddenWithAlly", "killParticipation",
    "killsNearEnemyTurret", "killsOnOtherLanesEarlyJungleAsLaner", "killsUnderOwnTurret",
    "knockEnemyIntoTeamAndKill", "landSkillShotsEarlyGame", "laningPhaseGoldExpAdvantage",
    "riftHeraldTakedowns", "soloKills", "survivedSingleDigitHpCount", "survivedThreeImmobilizesInFight",
    "takedowns", "takedownsBeforeJungleMinionSpawn", "takedownsInAlcove", "teamBaronKills",
    "teamDamagePercentage", "teamRiftHeraldKills", "turretTakedowns", "voidMonsterKill"
]

df = pd.read_csv(file_name)
dados_finais = []
total = len(df)
validas = 0
falhas = 0

def tem_smite(j):
    return j['summoner1Id'] == 11 or j['summoner2Id'] == 11

print(f"🔍 Iniciando processamento de {total} partidas (KEY_ID {key_id})")

for i, row in df.iterrows():
    match_id = row['Game']
    region = row['Region']
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 429:
            print(f"⏳ Rate limit atingido. Aguardando 2 minutos...")
            time.sleep(120)
            resp = requests.get(url)

        if resp.status_code != 200:
            print(f"❌ Erro {resp.status_code} - {match_id}")
            falhas += 1
            continue

        partida = resp.json()
        jogadores = partida['info']['participants']
        j1 = jogadores[1]
        j2 = jogadores[6]

        if not (tem_smite(j1) and tem_smite(j2)):
            falhas += 1
            continue
        if j1.get('timePlayed', 0) < 600 or j2.get('timePlayed', 0) < 600:
            falhas += 1
            continue
        if any(p.get('timePlayed', 0) < 600 for p in jogadores):
            falhas += 1
            continue
        if any(p.get('gameEndedInEarlySurrender', False) for p in jogadores):
            falhas += 1
            continue

        for j in [j1, j2]:
            dados = {k: j.get(k) for k in importante + not_challenges}
            dados.update({k: j['challenges'].get(k) for k in challenges})
            dados['win'] = j.get('win')
            dados['teamId'] = j.get('teamId')
            dados_finais.append(dados)

        validas += 1

    except Exception as e:
        print(f"💥 Erro em {match_id}: {e}")
        falhas += 1

    if (i + 1) % 10 == 0 or i + 1 == total:
        taxa = 100 * validas / (validas + falhas) if validas + falhas else 0
        print(f"✔️ {i+1}/{total} partidas processadas | ✅ válidas: {validas} | ❌ falhas: {falhas} | 🎯 taxa: {taxa:.2f}%")

# Salvar CSV
output_dir = os.path.join(os.path.dirname(__file__), "csv_estatisticas")
os.makedirs(output_dir, exist_ok=True)
saida = os.path.join(output_dir, f"dados_junglers_part_{key_id}.csv")
pd.DataFrame(dados_finais).to_csv(saida, index=False)
print(f"✅ Resultado salvo: {saida}")