
import requests
import time
from keys import API_KEYS
import pandas as pd

api_key = API_KEYS[0]


csv_path = r"C:\\Users\\cesar\\Desktop\\trabalhos puc\\Trabalho Engenharia Social LoL\\dados e afins\\games_with_regions_final.csv"

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

df = pd.read_csv(csv_path)
amostras = df.head(10).to_dict(orient='records')

def processar_partida(match_id, region):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 429:
            print("Rate limit excedido, aguardando 2 minutos...")
            time.sleep(120)
            resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Erro {resp.status_code} ao buscar {match_id}")
            return

        partida = resp.json()
        jogadores = partida['info']['participants']
        j1 = jogadores[1]
        j2 = jogadores[6]

        def tem_smite(j):
            return j['summoner1Id'] == 11 or j['summoner2Id'] == 11

        if not (tem_smite(j1) and tem_smite(j2)):
            print(f"❌ {match_id} descartado: jungler sem Smite")
            return

        if j1.get('timePlayed', 0) < 600 or j2.get('timePlayed', 0) < 600:
            print(f"❌ {match_id} descartado: jungler AFK")
            return

        if any(p.get('timePlayed', 0) < 600 for p in jogadores):
            print(f"❌ {match_id} descartado: jogador AFK no time")
            return

        if any(p.get('gameEndedInEarlySurrender', False) for p in jogadores):
            print(f"❌ {match_id} descartado: rendição antecipada")
            return

        print(f"✅ {match_id} válido:")
        for i, jungler in enumerate([j1, j2], start=1):
            dados = {k: jungler.get(k) for k in importante + not_challenges}
            dados.update({k: jungler['challenges'].get(k) for k in challenges})
            dados['win'] = jungler.get('win')
            dados['teamId'] = jungler.get('teamId')
            print(f"  Jungler {i}:")
            for k, v in dados.items():
                print(f"    {k}: {v}")
            print()

    except Exception as e:
        print(f"Erro em {match_id}: {e}")

for item in df.head(10).to_dict(orient='records'):
    processar_partida(item['Game'], item['Region'])