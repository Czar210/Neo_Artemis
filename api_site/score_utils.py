import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, 'banco_jogadores.db')

VARIAVEIS_RELEVANTES = [
    'kills', 'soloKills', 'damagePerMinute', 'killParticipation',
    'killsNearEnemyTurret', 'killsOnOtherLanesEarlyJungleAsLaner', 'killsUnderOwnTurret', 'quadraKills', 'takedowns',
    'visionScore', 'wardsPlaced', 'wardsKilled', 'controlWardsPlaced',
    'objectivesStolen', 'epicMonsterSteals', 'baronKills', 'dragonTakedowns',
    'riftHeraldTakedowns', 'epicMonsterKillsNearEnemyJungler', 'epicMonsterKillsWithin30SecondsOfSpawn',
    'goldEarned', 'goldPerMinute', 'champExperience', 'jungleCsBefore10Minutes',
    'initialBuffCount', 'initialCrabCount', 'totalAllyJungleMinionsKilled',
    'alliedJungleMonsterKills', 'totalEnemyJungleMinionsKilled', 'enemyJungleMonsterKills',
    'damageDealtToBuildings', 'damageDealtToObjectives', 'turretKills', 'inhibitorKills', 'turretTakedowns',
    'teamRiftHeraldKills', 'teamBaronKills',
    'deaths', 'assists', 'totalDamageTaken', 'longestTimeSpentLiving',
    'survivedSingleDigitHpCount', 'survivedThreeImmobilizesInFight', 'kda',
    'totalTimeCCDealt', 'enemyChampionImmobilizations', 'immobilizeAndKillWithAlly',
    'knockEnemyIntoTeamAndKill', 'landSkillShotsEarlyGame',
    'earlyLaningPhaseGoldExpAdvantage', 'laningPhaseGoldExpAdvantage',
    'takedownsBeforeJungleMinionSpawn', 'voidMonsterKill', 'totalDamageDealtToChampions'
]

def puxar_partidas_jogador(nickname):
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM partidas_jogadores WHERE nickname = ?"
    df = pd.read_sql_query(query, conn, params=(nickname.lower(),))
    conn.close()
    return None if df.empty else df

def puxar_scores_salvos(nickname):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            "Agressividade", "Controle de Mapa", "Eficiência de Recursos", 
            "Pressão em Estruturas", "Sustentação e Sobrevivência",
            "Impacto Utilitário", "Impacto no Early Game", "Controle de Objetivos"
        FROM scores_jogadores 
        WHERE LOWER(nickname) = LOWER(?)
    ''', (nickname,))
    row = cursor.fetchone()
    conn.close()
    if row:
        colunas = ['Agressividade', 'Controle de Mapa', 'Eficiência de Recursos', 
                   'Pressão em Estruturas', 'Sustentação e Sobrevivência',
                   'Impacto Utilitário', 'Impacto no Early Game', 'Controle de Objetivos']
        return dict(zip(colunas, row))
    else:
        return None

def calcular_scores_jogador(df):
    if df is None or df.empty:
        return None

    scores = {}

    scores['Agressividade'] = df[['kills', 'soloKills', 'damagePerMinute', 'killParticipation',
                                  'killsNearEnemyTurret', 'killsOnOtherLanesEarlyJungleAsLaner',
                                  'killsUnderOwnTurret', 'quadraKills', 'takedowns']].mean().mean() * 10

    scores['Controle de Mapa'] = df[['visionScore', 'wardsPlaced', 'wardsKilled', 'controlWardsPlaced',
                                     'objectivesStolen', 'epicMonsterSteals', 'baronKills', 'dragonTakedowns',
                                     'riftHeraldTakedowns', 'epicMonsterKillsNearEnemyJungler',
                                     'epicMonsterKillsWithin30SecondsOfSpawn']].mean().mean() * 10

    scores['Eficiência de Recursos'] = df[['goldEarned', 'goldPerMinute', 'champExperience',
                                           'jungleCsBefore10Minutes', 'initialBuffCount', 'initialCrabCount',
                                           'totalAllyJungleMinionsKilled', 'alliedJungleMonsterKills',
                                           'totalEnemyJungleMinionsKilled', 'enemyJungleMonsterKills']].mean().mean() * 10

    scores['Pressão em Estruturas'] = df[['damageDealtToBuildings', 'damageDealtToObjectives',
                                          'turretKills', 'inhibitorKills', 'turretTakedowns',
                                          'teamRiftHeraldKills', 'teamBaronKills']].mean().mean() * 10

    scores['Sustentação e Sobrevivência'] = (
    df[['totalDamageTaken', 'longestTimeSpentLiving',
        'survivedSingleDigitHpCount', 'survivedThreeImmobilizesInFight', 'kda']].mean().mean()- df['deaths'].mean() * 0.5) * 10

    scores['Impacto Utilitário'] = df[['totalTimeCCDealt', 'enemyChampionImmobilizations',
                                       'immobilizeAndKillWithAlly', 'knockEnemyIntoTeamAndKill',
                                       'landSkillShotsEarlyGame']].mean().mean() * 10

    scores['Impacto no Early Game'] = df[['earlyLaningPhaseGoldExpAdvantage',
                                          'laningPhaseGoldExpAdvantage', 'takedownsBeforeJungleMinionSpawn']].mean().mean() * 10

    scores['Controle de Objetivos'] = df[['voidMonsterKill', 'epicMonsterKillsNearEnemyJungler',
                                          'epicMonsterKillsWithin30SecondsOfSpawn', 'epicMonsterSteals',
                                          'baronKills', 'dragonTakedowns', 'riftHeraldTakedowns']].mean().mean() * 10

    # Clipar scores entre 0 e 10
    for k in scores:
        scores[k] = min(max(scores[k], 0), 10)

    return scores
