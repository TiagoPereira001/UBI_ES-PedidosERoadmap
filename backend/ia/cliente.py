"""Escolhe o serviço de IA e devolve a resposta em JSON. É o único sítio que decide qual se usa."""

import json

from django.conf import settings

from . import claude, gemini, lmstudio
from .erros import RespostaInvalida, SemIA

# Por esta ordem: sem IA_FORNECEDOR, usa-se o primeiro que estiver configurado. O local vem antes dos da rede.
FORNECEDORES = {"lmstudio": lmstudio, "gemini": gemini, "claude": claude}


def fornecedor():
    """Nome do serviço a usar ('lmstudio', 'gemini' ou 'claude'), ou None se nenhum estiver configurado."""
    escolhido = settings.IA_FORNECEDOR
    if escolhido:
        modulo = FORNECEDORES.get(escolhido)
        return escolhido if modulo and modulo.disponivel() else None
    return next((nome for nome, modulo in FORNECEDORES.items() if modulo.disponivel()), None)


def pedir_json(instrucoes, dados, esquema):
    """Envia as instruções e os dados (convertidos em JSON) e devolve (resposta em dict, serviço usado).

    `esquema` é o JSON Schema que a resposta tem de seguir. Lança SemIA se não houver serviço,
    RespostaInvalida se a resposta não for JSON, e deixa passar os erros de rede e de tempo limite.
    """
    nome = fornecedor()
    if nome is None:
        raise SemIA("Não há nenhum serviço de IA configurado.")
    texto = FORNECEDORES[nome].pedir(instrucoes, json.dumps(dados, ensure_ascii=False), esquema)
    try:
        return json.loads(texto), nome
    except ValueError as erro:
        raise RespostaInvalida(f"O serviço {nome} não devolveu JSON.") from erro
