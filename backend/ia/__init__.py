"""Ligação aos serviços de IA (decisões D4, D8 e D9 em wiki/04-arquitetura/decisoes.md).

Os módulos do produto não falam diretamente com nenhum serviço: chamam `ia.cliente.pedir_json`,
que escolhe o serviço configurado (Gemma 4 no LM Studio, Gemini ou Claude), envia as instruções e os dados, e devolve
a resposta já em JSON. Quem chama valida a resposta e tem sempre uma alternativa local para
quando não há IA (`SemIA`) ou ela falha.

Para ligar um serviço basta uma variável de ambiente (ver backend/.env.example): LMSTUDIO_URL para
o modelo local, que não precisa de chave; GEMINI_API_KEY para o Gemini, ANTHROPIC_API_KEY para
o Claude. Sem nenhuma, nada é enviado.
"""
