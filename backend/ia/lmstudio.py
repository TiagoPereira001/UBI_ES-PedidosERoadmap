"""Modelo local (Gemma 4) no LM Studio, pela API compatível com a da OpenAI. Só a biblioteca padrão do Python.

Corre no computador da equipa: não precisa de chave e os dados não saem daqui. Por isso só se aceitam
endereços locais em LMSTUDIO_URL. Se no LM Studio se ligar a autenticação, o token vai em
LMSTUDIO_API_KEY (no .env) e segue só no cabeçalho.
"""

import json
import os
import urllib.request
from urllib.parse import urlsplit

from django.conf import settings

from .erros import RespostaInvalida

# host.docker.internal é o próprio computador, visto de dentro de um contentor.
LOCAIS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}

# Sem proxies: com um proxy configurado, o pedido (e o token) podiam sair do computador.
_abrir = urllib.request.build_opener(urllib.request.ProxyHandler({})).open


def disponivel():
    endereco = urlsplit(settings.LMSTUDIO_URL)
    return endereco.scheme == "http" and endereco.hostname in LOCAIS


def pedir(instrucoes, texto, esquema):
    cabecalhos = {"Content-Type": "application/json"}
    if os.environ.get("LMSTUDIO_API_KEY"):
        cabecalhos["Authorization"] = f"Bearer {os.environ['LMSTUDIO_API_KEY']}"
    corpo = {
        "model": settings.LMSTUDIO_MODELO,
        "messages": [{"role": "system", "content": instrucoes}, {"role": "user", "content": texto}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "resposta", "strict": True, "schema": esquema},
        },
        "temperature": 0.2,
    }
    pedido = urllib.request.Request(
        f"{settings.LMSTUDIO_URL.rstrip('/')}/v1/chat/completions",
        data=json.dumps(corpo).encode(),
        headers=cabecalhos,
        method="POST",
    )
    # O modelo corre no computador, por isso leva mais tempo do que um serviço na rede.
    with _abrir(pedido, timeout=settings.LMSTUDIO_TEMPO_LIMITE) as resposta:
        dados = json.load(resposta)
    escolhas = dados.get("choices") or []
    if not escolhas or escolhas[0].get("finish_reason") != "stop":
        raise RespostaInvalida("O modelo local não acabou a resposta.")
    return escolhas[0]["message"]["content"]
