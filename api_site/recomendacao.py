# recomendacao.py

import pandas as pd
import numpy as np
import os
from score_utils import puxar_scores_salvos

# =============================
# Função 1 - Recomendação para jogador real (nickname)
# =============================

def recomendar_campeoes(nickname):
    BASE_DIR = os.path.dirname(__file__)

    # Caminhos para os CSVs
    caminho_win = os.path.join(BASE_DIR, 'scores_campeoes_win.csv')
    caminho_lose = os.path.join(BASE_DIR, 'scores_campeoes_lose.csv')

    colunas_relevantes = [
        'Agressividade', 'Controle de Mapa', 'Eficiência de Recursos',
        'Pressão em Estruturas', 'Sustentação e Sobrevivência',
        'Impacto Utilitário', 'Impacto no Early Game', 'Controle de Objetivos'
    ]

    # Carregar dados dos campeões
    df_win = pd.read_csv(caminho_win)
    df_lose = pd.read_csv(caminho_lose)

    df_win.set_index('championName', inplace=True)
    df_lose.set_index('championName', inplace=True)

    # Média entre win e lose
    df_media = (df_win[colunas_relevantes] + df_lose[colunas_relevantes]) / 2
    df_media.reset_index(inplace=True)

    # Buscar scores do jogador
    scores_jogador = puxar_scores_salvos(nickname.lower())
    if not scores_jogador:
        return None

    vetor_jogador = np.array([scores_jogador[col] for col in colunas_relevantes])

    recomendacoes = []

    for _, row in df_media.iterrows():
        vetor_campeao = np.array([row[col] for col in colunas_relevantes])

        if np.linalg.norm(vetor_jogador) == 0 or np.linalg.norm(vetor_campeao) == 0:
            similaridade = 0
        else:
            similaridade = np.dot(vetor_jogador, vetor_campeao) / (np.linalg.norm(vetor_jogador) * np.linalg.norm(vetor_campeao))

        recomendacoes.append({
            'campeao': row['championName'],
            'similaridade': round(similaridade * 10, 2)
        })

    recomendacoes = sorted(recomendacoes, key=lambda x: x['similaridade'], reverse=True)

    return recomendacoes

# =============================
# Função 2 - Recomendação para jogadores do Quiz
# =============================

def recomendar_campeoes_quiz(scores_quiz):
    BASE_DIR = os.path.dirname(__file__)

    caminho_win = os.path.join(BASE_DIR, 'scores_campeoes_win.csv')
    caminho_lose = os.path.join(BASE_DIR, 'scores_campeoes_lose.csv')

    colunas_relevantes = [
        'Agressividade', 'Controle de Mapa', 'Eficiência de Recursos',
        'Pressão em Estruturas', 'Sustentação e Sobrevivência',
        'Impacto Utilitário', 'Impacto no Early Game', 'Controle de Objetivos'
    ]

    df_win = pd.read_csv(caminho_win)
    df_lose = pd.read_csv(caminho_lose)

    df_win.set_index('championName', inplace=True)
    df_lose.set_index('championName', inplace=True)

    df_media = (df_win[colunas_relevantes] + df_lose[colunas_relevantes]) / 2
    df_media.reset_index(inplace=True)

    vetor_jogador = np.array([scores_quiz[col] for col in colunas_relevantes])

    recomendacoes = []

    for _, row in df_media.iterrows():
        vetor_campeao = np.array([row[col] for col in colunas_relevantes])

        if np.linalg.norm(vetor_jogador) == 0 or np.linalg.norm(vetor_campeao) == 0:
            similaridade = 0
        else:
            similaridade = np.dot(vetor_jogador, vetor_campeao) / (np.linalg.norm(vetor_jogador) * np.linalg.norm(vetor_campeao))

        recomendacoes.append({
            'campeao': row['championName'],
            'similaridade': round(similaridade * 10, 2)
        })

    recomendacoes = sorted(recomendacoes, key=lambda x: x['similaridade'], reverse=True)

    return recomendacoes

# =============================
# Para Teste Direto
# =============================

if __name__ == "__main__":
    exemplo_nickname = "seu_nick_aqui"
    recomendados = recomendar_campeoes(exemplo_nickname)
    for rec in recomendados[:10]:
        print(f"{rec['campeao']}: {rec['similaridade']}/10")
