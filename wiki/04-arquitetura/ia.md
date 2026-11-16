# IA no sistema

[Índice](../README.md) · [← Desenho de software](desenho.md) · [Casos de uso →](../05-modelacao/casos-de-uso.md)

O enunciado pede "AI-assisted prioritization suggestions" e "automatic generation of User Stories". Esta página explica como o sistema fala com um serviço de IA, como se liga uma chave e o que acontece quando não há nenhuma. As decisões estão em [D4](decisoes.md#d4-a-ia-fica-atrás-de-um-adaptador-23102026) e [D8](decisoes.md#d8-gemini-e-claude-atrás-do-mesmo-cliente-16112026).

## Como está montado

```
ecrã 05 (Priorização)  ──►  priorizacao/ia.py  ──►  ia/cliente.py  ──►  ia/gemini.py  ──►  Google
                                   │                      │            ia/claude.py  ──►  Anthropic
                                   │                      └─ sem chave: SemIA
                                   └─ SemIA, erro ou resposta errada: regra local
```

| Peça | O que faz |
|---|---|
| `backend/ia/cliente.py` | Escolhe o serviço e devolve a resposta já em JSON. É o único sítio que sabe que serviços existem. |
| `backend/ia/gemini.py` | Faz o pedido ao Gemini pela API REST, só com a biblioteca padrão do Python. A chave vai num cabeçalho, nunca no endereço. |
| `backend/ia/claude.py` | Faz o pedido ao Claude pelo pacote `anthropic`, com saída estruturada. |
| `backend/priorizacao/ia.py` | Monta o pedido (instruções, dados dos pedidos e esquema da resposta), valida a resposta e, se alguma coisa falhar, usa a regra local. |

Qualquer módulo que precise de IA faz o mesmo que a priorização: chama `pedir_json(instrucoes, dados, esquema)`, valida o que vem e tem uma alternativa local. No Sprint 5, a geração de user stories (ecrã 10) usa o mesmo cliente.

## Qual serviço se usa

| Chaves definidas | Serviço |
|---|---|
| Nenhuma | Nenhum: regra local, sem rede e sem custos (é o que acontece hoje) |
| `GEMINI_API_KEY` | Gemini |
| `ANTHROPIC_API_KEY` | Claude |
| As duas | Gemini, a não ser que `IA_FORNECEDOR=claude` |

O modelo de cada serviço também se escolhe por variável: `GEMINI_MODELO` e `IA_MODELO` (por omissão `claude-opus-5-5`).

Para o Gemini usamos por omissão o `gemini-3.5-flash-lite`: é o modelo mais barato e o que tem mais pedidos por dia no plano gratuito (em novembro de 2026, cerca de 500 por dia, contra 20 do Gemini 3.8 Flash). Para sugerir uma ordem ou escrever user stories chega. Os limites gratuitos mudam com frequência e contam por projeto e por modelo; os números certos estão no Google AI Studio.

## Ligar uma chave

1. Criar a chave: Gemini em [aistudio.google.com/apikey](https://aistudio.google.com/apikey); Claude em [console.anthropic.com](https://console.anthropic.com) (pago por utilização).
2. Na raiz do repositório, criar um ficheiro `.env` com uma linha (o `.env` está no `.gitignore` e nunca vai para o GitHub):

   ```
   GEMINI_API_KEY=a-chave-que-a-google-deu
   ```

3. Arrancar como sempre: `docker compose up --build`. O Docker lê o `.env` e passa a chave ao contentor `backend`.
4. Entrar como `ricardo` (Product Owner), abrir a Priorização e carregar em **Pedir sugestão da IA**. O post-it diz "Sugestão feita pelo Gemini (Google)". Se disser "regra local", a chave não chegou ou o serviço falhou; o motivo aparece no terminal do back-end.

Sem Docker, basta exportar a variável no terminal antes do `runserver`: `export GEMINI_API_KEY=...`.

## O que se envia

Na priorização vão só o número, o título, os votos, o impacto e o esforço de cada pedido. Não vão descrições, nomes de pessoas nem comentários. No plano gratuito, a Google pode usar o que recebe para melhorar os modelos: os nossos dados são de exemplo, mas num caso real era preciso o plano pago ou outro serviço.

## Como se testa

Nenhum teste chama a Google nem a Anthropic. Os testes em `backend/ia/tests/` simulam a resposta do Gemini e verificam o endereço, o cabeçalho com a chave, o tempo limite e o que acontece com respostas cortadas ou que não são JSON. Os testes da priorização simulam o cliente e verificam que uma falha leva sempre à regra local.

## Ver também

- [Registo de decisões](decisoes.md)
- [Desenho de software](desenho.md)
- [Testes](../06-codigo/testes.md)
