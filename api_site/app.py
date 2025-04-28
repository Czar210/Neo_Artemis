# app.py

from flask import Flask, request, jsonify, render_template, redirect, url_for
from call_api_riot import buscar_puuid, buscar_partidas, buscar_detalhes_partida, extrair_estatisticas
from normalizacao import normalizar_estatisticas
from database import criar_tabelas, inserir_partida, salvar_scores
from score_utils import puxar_partidas_jogador, calcular_scores_jogador, puxar_scores_salvos
from recomendacao import recomendar_campeoes
import os
import sqlite3
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar app Flask
app = Flask(__name__)

# Caminho para o banco
BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, 'banco_jogadores.db')

# =============================
# Rotas da API (JSON)
# =============================

# Filtro para formatar scores em notas de letra
@app.template_filter('format_score')
def format_score_filter(score):
    try:
        score = float(score)
        if score >= 9.8:
            return "S"
        elif score >= 8.5:
            return "A+"
        elif score >= 7.5:
            return "A"
        elif score >= 6.5:
            return "B+"
        elif score >= 5.5:
            return "B"
        elif score >= 4.5:
            return "C+"
        elif score >= 3.5:
            return "C"
        elif score >= 2.5:
            return "D+"
        else:
            return "D"

    except:
        return "-"
        
# Função para gerar scores baseados nas respostas do Quiz
def gerar_scores_quiz(respostas):
    scores = {}
    scores['Agressividade'] = (respostas[0] + respostas[6] + respostas[9] + respostas[11] + respostas[15]) / 5
    scores['Controle de Mapa'] = (respostas[2] + respostas[7] + respostas[14] + respostas[16]) / 4
    scores['Eficiência de Recursos'] = (respostas[1] + respostas[17]) / 2
    scores['Pressão em Estruturas'] = (respostas[4] + respostas[10]) / 2
    scores['Sustentação e Sobrevivência'] = (respostas[8] + respostas[13]) / 2
    scores['Impacto Utilitário'] = (respostas[5] + respostas[12]) / 2
    scores['Impacto no Early Game'] = (respostas[3] + respostas[9]) / 2
    scores['Controle de Objetivos'] = (respostas[3] + respostas[7] + respostas[16]) / 3

    for k in scores:
        scores[k] = round((scores[k] - 1) * (10 / 4), 2)  # Escala 1-5 para 0-10

    return scores


@app.route('/analisar_jogador', methods=['POST'])
def analisar_jogador():
    """Puxa partidas do jogador, normaliza e salva no banco."""
    data = request.json
    nome = data.get('nome')
    tag = data.get('tag')
    plataforma = data.get('platform')
    partidas_requeridas = data.get('quantidade', 30)

    if not nome or not tag or not plataforma:
        return jsonify({'erro': 'Nome, tag e plataforma são obrigatórios'}), 400

    try:
        puuid = buscar_puuid(nome, tag, plataforma)
        partidas_ids = buscar_partidas(puuid, plataforma, quantidade=100)

        partidas_salvas = 0

        for match_id in partidas_ids:
            partida = buscar_detalhes_partida(match_id, plataforma)
            estatisticas = extrair_estatisticas(partida, puuid)

            if estatisticas is None:
                continue  # Ignora partidas sem Smite

            try:
                estatisticas_normalizadas = normalizar_estatisticas(estatisticas)
            except Exception as e:
                print(f"Ignorando partida: {e}")
                continue

            estatisticas_normalizadas['nickname'] = nome.lower()
            estatisticas_normalizadas['platform'] = plataforma

            inserir_partida(estatisticas_normalizadas)
            partidas_salvas += 1

            if partidas_salvas >= partidas_requeridas:
                break

        if partidas_salvas < partidas_requeridas:
            return jsonify({'erro': f'Jogador possui apenas {partidas_salvas} partidas válidas.'}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM partidas_jogadores WHERE nickname = ?", (nome.lower(),))
        contagem = cursor.fetchone()[0]
        print(f"📝 Partidas salvas para {nome.lower()}: {contagem}")
        conn.close()

        return jsonify({'mensagem': f'{partidas_salvas} partidas normalizadas e salvas com sucesso!'}), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/scores', methods=['GET'])
def scores():
    """Calcula e retorna os scores do jogador."""
    nickname = request.args.get('nickname')
    if not nickname:
        return jsonify({'erro': 'Nickname é obrigatório'}), 400

    try:
        nickname = nickname.lower()

        scores_salvos = puxar_scores_salvos(nickname)
        if scores_salvos:
            return jsonify(scores_salvos)

        df_partidas = puxar_partidas_jogador(nickname)
        scores_resultado = calcular_scores_jogador(df_partidas)

        if scores_resultado is None:
            return jsonify({'erro': 'Nenhuma partida encontrada para o jogador.'}), 404

        salvar_scores(nickname, scores_resultado)
        return jsonify(scores_resultado)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/recomendar', methods=['GET'])
def recomendar():
    """Recomenda campeões baseados nos pontos fortes do jogador."""
    nickname = request.args.get('nickname')
    if not nickname:
        return jsonify({'erro': 'Nickname é obrigatório'}), 400

    try:
        recomendacoes = recomendar_campeoes(nickname)
        if recomendacoes is None:
            return jsonify({'erro': 'Jogador não encontrado ou sem scores calculados.'}), 404
        return jsonify(recomendacoes)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# =============================
# Rotas de Front-End (HTML)
# =============================

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

from recomendacao import recomendar_campeoes_quiz

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    perguntas = [
        "Gosto de arriscar jogadas para conseguir abates.",
        "Prefiro farmar de forma segura ao invés de lutar.",
        "Dou muita importância ao controle de visão do mapa.",
        "Priorizar dragões e barões é crucial para vencer.",
        "Prefiro proteger estruturas do meu time a buscar abates.",
        "Gosto de aplicar controle de grupo nos inimigos.",
        "Busco invadir a selva inimiga sempre que possível.",
        "Dou prioridade em ajudar o time a garantir objetivos.",
        "Prefiro ter uma alta taxa de sobrevivência nas lutas.",
        "Foco em obter vantagem logo no início do jogo.",
        "Gosto de split-push (forçar torres em rotas separadas).",
        "Gosto de estratégias de emboscada (ganks).",
        "Prefiro campeões que causam dano ao longo do tempo (DPS) do que burst.",
        "Mantenho a calma mesmo quando o jogo está difícil.",
        "Tenho paciência para planejar controle de mapa e rotações.",
        "Dou preferência a campeões de alta mobilidade.",
        "Priorizar visão (wards e sentinelas) é essencial para meu estilo.",
        "Prezo por eficiência em farm, mesmo que signifique evitar brigas.",
        "Busco vencer no macro (estratégia) ao invés de só na luta direta.",
        "Prefiro decisões calculadas a jogadas impulsivas."
    ]

    if request.method == 'POST':
        respostas = [int(request.form[f'p{i}']) for i in range(1, 21)]
        scores = gerar_scores_quiz(respostas)
        recomendacoes = recomendar_campeoes_quiz(scores)
        return render_template('resultados_quiz.html', scores=scores, recomendacoes=recomendacoes, nickname="Jogador do Quiz")

    return render_template('quiz.html', perguntas=perguntas)


@app.route('/tabela_campeoes', methods=['GET'])
def tabela_campeoes():
    import pandas as pd
    import os

    BASE_DIR = os.path.dirname(__file__)

    caminho_win = os.path.join(BASE_DIR, 'scores_campeoes_win.csv')
    caminho_lose = os.path.join(BASE_DIR, 'scores_campeoes_lose.csv')

    df_win = pd.read_csv(caminho_win)
    df_lose = pd.read_csv(caminho_lose)

    colunas_relevantes = [
        'Agressividade', 'Controle de Mapa', 'Eficiência de Recursos', 
        'Pressão em Estruturas', 'Sustentação e Sobrevivência',
        'Impacto Utilitário', 'Impacto no Early Game', 'Controle de Objetivos'
    ]

    df_win.set_index('championName', inplace=True)
    df_lose.set_index('championName', inplace=True)

    df_media = (df_win[colunas_relevantes] + df_lose[colunas_relevantes]) / 2
    df_media.reset_index(inplace=True)

    # 🔥 Transformação correta (linear)
    for coluna in colunas_relevantes:
        df_media[coluna] = (df_media[coluna] + 1) * 5

    df_media.sort_values('championName', inplace=True)

    campeoes = df_media.to_dict(orient='records')

    return render_template('tabela_campeoes.html', campeoes=campeoes)

    
@app.route('/resultados', methods=['POST'])
def resultados():
    nickname = request.form.get('nickname')
    tag = request.form.get('tag')
    servidor = request.form.get('servidor')
    quantidade = int(request.form.get('quantidade', 30))

    if not nickname or not tag or not servidor:
        return redirect(url_for('home'))

    nickname = nickname.strip().lower()
    tag = tag.strip().upper()
    servidor = servidor.strip().lower()

    # Buscar scores
    scores = puxar_scores_salvos(nickname)

    if not scores:
        # Se não encontrar scores, tentar buscar partidas da API
        try:
            puuid = buscar_puuid(nickname, tag, servidor)
            partidas_ids = buscar_partidas(puuid, servidor, quantidade=quantidade)

            partidas_salvas = 0

            for match_id in partidas_ids:
                partida = buscar_detalhes_partida(match_id, servidor)
                estatisticas = extrair_estatisticas(partida, puuid)

                if estatisticas is None:
                    continue

                try:
                    estatisticas_normalizadas = normalizar_estatisticas(estatisticas)
                except Exception as e:
                    print(f"Ignorando partida: {e}")
                    continue

                estatisticas_normalizadas['nickname'] = nickname
                estatisticas_normalizadas['platform'] = servidor

                inserir_partida(estatisticas_normalizadas)
                partidas_salvas += 1

                if partidas_salvas >= quantidade:
                    break

            # Depois de salvar as partidas, calcular scores
            df_partidas = puxar_partidas_jogador(nickname)
            scores_calculados = calcular_scores_jogador(df_partidas)

            if scores_calculados:
                salvar_scores(nickname, scores_calculados)
                scores = puxar_scores_salvos(nickname)
            else:
                scores = None

        except Exception as e:
            print(f"Erro ao buscar jogador: {e}")
            scores = None

    # Buscar recomendações
    if scores:
        recomendacoes = recomendar_campeoes(nickname)
    else:
        recomendacoes = None

    return render_template('resultados.html', nickname=nickname, scores=scores, recomendacoes=recomendacoes)


# =============================
# Execução Principal
# =============================

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
