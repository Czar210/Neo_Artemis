import pandas as pd
import os

# Carregar bases M_Dias
BASE_DIR = os.path.dirname(__file__)

m_dias_win = pd.read_csv(os.path.join(BASE_DIR, 'M_dias_para_Win___True.csv'))
m_dias_lose = pd.read_csv(os.path.join(BASE_DIR, 'M_dias_para_Win___False.csv'))


def normalizar_estatisticas(estatisticas):
    """Normaliza as estatísticas de uma partida usando as médias de M_Dias."""
    champion = estatisticas.get('championName')
    win = estatisticas.get('win')

    if champion is None or win is None:
        raise ValueError("Estatísticas sem championName ou win definidos.")

    df_ref = m_dias_win if win == 1 else m_dias_lose

    ref_row = df_ref[df_ref['championName'] == champion]
    if ref_row.empty:
        raise ValueError(f"Campeão {champion} não encontrado na base M_Dias.")

    ref_row = ref_row.iloc[0]

    estatisticas_normalizadas = {}

    for key, value in estatisticas.items():
        if key in ref_row:
            referencia = ref_row[key]
            try:
                # Tenta converter para float
                valor_float = float(value)
                referencia_float = float(referencia)
                if referencia_float != 0:
                    estatisticas_normalizadas[key] = valor_float / referencia_float
                else:
                    estatisticas_normalizadas[key] = valor_float
            except (ValueError, TypeError):
                # Se não conseguir converter para float, apenas copia o valor original
                estatisticas_normalizadas[key] = value
        else:
            estatisticas_normalizadas[key] = value

    return estatisticas_normalizadas
