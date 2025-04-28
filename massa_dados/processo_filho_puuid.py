import os
import time
import pandas as pd
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do ambiente
load_dotenv()
api_key = os.getenv("API_KEY")
file_name = os.getenv("FILE_NAME")
key_id = os.getenv("KEY_ID")  # novo campo para identificar a chave usada

# Configurar log
log_file = f"log_{Path(file_name).stem}.txt"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

REQUEST_INTERVAL = 1.2

ERROR_MESSAGES = {
    400: "Bad request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Data not found",
    405: "Method not allowed",
    415: "Unsupported media type",
    429: "Rate limit exceeded",
    500: "Internal server error",
    502: "Bad gateway",
    503: "Service unavailable",
    504: "Gateway timeout"
}

try:
    summoners_data = pd.read_csv(file_name)
    if 'puuid' not in summoners_data.columns:
        summoners_data['puuid'] = ''
    summoners_data['Key_ID'] = key_id  # atribuir a chave usada
    last_request_time = 0
    total = len(summoners_data)
    print(f"Iniciando processamento de {total} registros para {file_name}...")

    for idx, (index, row) in enumerate(summoners_data.iterrows()):
        name = row['Name']
        tag = row['Tag']
        region = row['Region']
        server = row['Server']

        url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={api_key}"

        attempts = 0
        while attempts < 3:
            elapsed = time.time() - last_request_time
            if elapsed < REQUEST_INTERVAL:
                time.sleep(REQUEST_INTERVAL - elapsed)

            last_request_time = time.time()
            try:
                resp = requests.get(url, timeout=10)
                p_info = resp.json()
            except Exception as req_err:
                logging.error(f"Request failed for {name} ({server}): {req_err}")
                break

            if 'status' in p_info:
                status_code = p_info['status']['status_code']
                error_msg = ERROR_MESSAGES.get(status_code, "Unknown error")

                if status_code == 429:
                    logging.warning(f"{error_msg} for {name}. Waiting 60 seconds...")
                    time.sleep(60)
                    attempts += 1
                elif status_code == 404:
                    logging.info(f"{error_msg}: {name} ({server}) — removing entry.")
                    summoners_data.drop(index, inplace=True)
                    break
                else:
                    logging.error(f"{error_msg} ({status_code}) for {name}")
                    attempts += 1
            else:
                summoners_data.loc[index, 'puuid'] = p_info['puuid']
                logging.info(f"PUUID for {name} ({server}) added successfully.")
                print(f"[PUUID] {name} ({server}): {p_info['puuid']}")
                break

        if attempts == 3:
            logging.warning(f"Failed to retrieve PUUID for {name} after 3 attempts.")

        if (idx + 1) % 10 == 0:
            print(f"[{file_name}] Processados: {idx + 1}/{total}")

    summoners_data.to_csv(file_name, index=False)
    logging.info("File updated and saved successfully.")
    print(f"Finalizado {file_name}.")

    verificado = pd.read_csv(file_name)
    puuid_na = verificado['puuid'].isna().sum()
    print(f"[VERIFICAÇÃO] {len(verificado) - puuid_na}/{len(verificado)} PUUIDs salvos corretamente.")

except FileNotFoundError:
    logging.error(f"File not found: {file_name}")
except Exception as e:
    logging.exception(f"Unexpected error: {e}")