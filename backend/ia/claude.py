"""Claude, da Anthropic, pelo pacote oficial `anthropic`, com saída estruturada (JSON Schema)."""

import os

from django.conf import settings

from .erros import RespostaInvalida


def tem_chave():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def pedir(instrucoes, texto, esquema):
    import anthropic  # só se importa quando há chave, para o resto não depender do pacote

    cliente = anthropic.Anthropic(timeout=settings.IA_TEMPO_LIMITE, max_retries=0)
    resposta = cliente.beta.messages.create(
        model=settings.IA_MODELO,
        max_tokens=16000,
        # Se o modelo recusar, a API tenta outro modelo na mesma chamada.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": esquema}},
        system=instrucoes,
        messages=[{"role": "user", "content": texto}],
    )
    if resposta.stop_reason != "end_turn":
        raise RespostaInvalida(f"O Claude parou com '{resposta.stop_reason}'.")
    return next(bloco.text for bloco in resposta.content if bloco.type == "text")
