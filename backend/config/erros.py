"""Tradução das exceções do domínio para respostas HTTP da API."""

from rest_framework.response import Response
from rest_framework.views import exception_handler

from pedidos.servicos import RegraViolada, SemPermissao


def tratar_excecao(exc, context):
    if isinstance(exc, SemPermissao):
        return Response({"erro": str(exc)}, status=403)
    if isinstance(exc, RegraViolada):
        return Response({"erro": str(exc)}, status=400)
    return exception_handler(exc, context)
