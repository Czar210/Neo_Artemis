# database.py

import sqlite3
import os

# Caminho para o banco
BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, 'banco_jogadores.db')

# 🔑 Funções do Banco de Dados

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela de partidas dos jogadores (estatísticas normalizadas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidas_jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT,
            platform TEXT,
            championName TEXT,
            win INTEGER,
            -- Estatísticas normalizadas
            kills REAL, soloKills REAL, damagePerMinute REAL, killParticipation REAL,
            killsNearEnemyTurret REAL, killsOnOtherLanesEarlyJungleAsLaner REAL,
            killsUnderOwnTurret REAL, quadraKills REAL, takedowns REAL,
            visionScore REAL, wardsPlaced REAL, wardsKilled REAL, controlWardsPlaced REAL,
            objectivesStolen REAL, epicMonsterSteals REAL, baronKills REAL, dragonTakedowns REAL,
            riftHeraldTakedowns REAL, epicMonsterKillsNearEnemyJungler REAL,
            epicMonsterKillsWithin30SecondsOfSpawn REAL, goldEarned REAL, goldPerMinute REAL,
            champExperience REAL, jungleCsBefore10Minutes REAL, initialBuffCount REAL,
            initialCrabCount REAL, totalAllyJungleMinionsKilled REAL, alliedJungleMonsterKills REAL,
            totalEnemyJungleMinionsKilled REAL, enemyJungleMonsterKills REAL, damageDealtToBuildings REAL,
            damageDealtToObjectives REAL, turretKills REAL, inhibitorKills REAL, turretTakedowns REAL,
            teamRiftHeraldKills REAL, teamBaronKills REAL, deaths REAL, assists REAL, totalDamageTaken REAL,
            longestTimeSpentLiving REAL, survivedSingleDigitHpCount REAL, survivedThreeImmobilizesInFight REAL,
            kda REAL, totalTimeCCDealt REAL, enemyChampionImmobilizations REAL, immobilizeAndKillWithAlly REAL,
            knockEnemyIntoTeamAndKill REAL, landSkillShotsEarlyGame REAL,
            earlyLaningPhaseGoldExpAdvantage REAL, laningPhaseGoldExpAdvantage REAL,
            takedownsBeforeJungleMinionSpawn REAL, voidMonsterKill REAL, totalDamageDealtToChampions REAL
        )
    ''')

    # Tabela de scores do jogador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores_jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE,
            "Agressividade" REAL,
            "Controle de Mapa" REAL,
            "Eficiência de Recursos" REAL,
            "Pressão em Estruturas" REAL,
            "Sustentação e Sobrevivência" REAL,
            "Impacto Utilitário" REAL,
            "Impacto no Early Game" REAL,
            "Controle de Objetivos" REAL
        )
    ''')

    conn.commit()
    conn.close()

def inserir_partida(dados_partida):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    dados_partida['nickname'] = dados_partida['nickname'].lower()

    placeholders = ', '.join(['?'] * len(dados_partida))
    colunas = ', '.join(dados_partida.keys())

    sql = f'INSERT INTO partidas_jogadores ({colunas}) VALUES ({placeholders})'
    valores = list(dados_partida.values())

    cursor.execute(sql, valores)

    conn.commit()
    conn.close()

def salvar_scores(nickname, scores):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    nickname = nickname.lower()

    cursor.execute('''
        INSERT INTO scores_jogadores (nickname, "Agressividade", "Controle de Mapa", "Eficiência de Recursos", "Pressão em Estruturas",
            "Sustentação e Sobrevivência", "Impacto Utilitário", "Impacto no Early Game", "Controle de Objetivos")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(nickname) DO UPDATE SET
            "Agressividade"=excluded."Agressividade",
            "Controle de Mapa"=excluded."Controle de Mapa",
            "Eficiência de Recursos"=excluded."Eficiência de Recursos",
            "Pressão em Estruturas"=excluded."Pressão em Estruturas",
            "Sustentação e Sobrevivência"=excluded."Sustentação e Sobrevivência",
            "Impacto Utilitário"=excluded."Impacto Utilitário",
            "Impacto no Early Game"=excluded."Impacto no Early Game",
            "Controle de Objetivos"=excluded."Controle de Objetivos"
    ''', (
        nickname,
        scores['Agressividade'],
        scores['Controle de Mapa'],
        scores['Eficiência de Recursos'],
        scores['Pressão em Estruturas'],
        scores['Sustentação e Sobrevivência'],
        scores['Impacto Utilitário'],
        scores['Impacto no Early Game'],
        scores['Controle de Objetivos']
    ))

    conn.commit()
    conn.close()


# Resetar banco (opcional)
def resetar_banco():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ Banco de dados '{DB_NAME}' apagado.")
    criar_tabelas()
    print(f"✅ Novo banco '{DB_NAME}' criado com sucesso.")

if __name__ == "__main__":
    criar_tabelas()
    print("✅ Tabelas criadas com sucesso!")
