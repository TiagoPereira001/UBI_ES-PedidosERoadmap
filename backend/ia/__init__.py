"""Ligação aos serviços de IA externos (decisões D4 e D8 em wiki/04-arquitetura/decisoes.md).

Os módulos do produto não falam com a Google nem com a Anthropic: chamam `ia.cliente.pedir_json`,
que escolhe o serviço configurado (Gemini ou Claude), envia as instruções e os dados, e devolve
a resposta já em JSON. Quem chama valida a resposta e tem sempre uma alternativa local para
quando não há IA (`SemIA`) ou ela falha.

Para ligar um serviço basta a chave numa variável de ambiente (ver backend/.env.example):
GEMINI_API_KEY para o Gemini, ANTHROPIC_API_KEY para o Claude. Sem nenhuma, nada é enviado.
"""
