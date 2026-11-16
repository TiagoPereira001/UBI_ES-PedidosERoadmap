"""Gemini, da Google, pela API REST (sem bibliotecas extra: só a biblioteca padrão do Python).

Documentação: https://ai.google.dev/api/generate-content
A chave vai num cabeçalho e nunca no endereço, para não ficar nos registos de acesso.
"""

import json
import os
import urllib.request

from django.conf import settings

from .erros import RespostaInvalida

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"


def tem_chave():
    return bool(os.environ.get("GEMINI_API_KEY"))


def pedir(instrucoes, texto, esquema):
    """Devolve o texto da resposta. O esquema vai nas instruções; a validação fica com quem chama."""
    corpo = {
        "systemInstruction": {
            "parts": [{"text": f"{instrucoes}\n\nResponde só com JSON que siga este esquema:\n{json.dumps(esquema)}"}]
        },
        "contents": [{"role": "user", "parts": [{"text": texto}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    pedido = urllib.request.Request(
        URL.format(modelo=settings.GEMINI_MODELO),
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        method="POST",
    )
    with urllib.request.urlopen(pedido, timeout=settings.IA_TEMPO_LIMITE) as resposta:
        dados = json.load(resposta)
    candidatos = dados.get("candidates") or []
    if not candidatos or candidatos[0].get("finishReason") != "STOP":
        raise RespostaInvalida("O Gemini não acabou a resposta.")
    return "".join(parte.get("text", "") for parte in candidatos[0]["content"]["parts"])
