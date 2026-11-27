# IA no sistema

[Índice](../README.md) · [← Desenho de software](desenho.md) · [Casos de uso →](../05-modelacao/casos-de-uso.md)

O enunciado pede "AI-assisted prioritization suggestions" e "automatic generation of User Stories". Esta página explica como o sistema fala com um serviço de IA, que serviço se usa e o que acontece quando não há nenhum. As decisões estão em [D4](decisoes.md#d4-a-ia-fica-atrás-de-um-adaptador-23102026), [D8](decisoes.md#d8-gemini-e-claude-atrás-do-mesmo-cliente-16112026) e [D9](decisoes.md#d9-gemma-4-no-computador-com-o-lm-studio-23112026).

## Como está montado

```
ecrã 05 (Priorização)  ──►  priorizacao/ia.py  ──►  ia/cliente.py  ──►  ia/lmstudio.py  ──►  Gemma 4, no computador
                                   │                      │            ia/gemini.py  ──►  Google
                                   │                      │            ia/claude.py  ──►  Anthropic
                                   │                      └─ nada configurado: SemIA
                                   └─ SemIA, erro ou resposta errada: regra local
```

| Peça | O que faz |
|---|---|
| `backend/ia/cliente.py` | Escolhe o serviço e devolve a resposta já em JSON. É o único sítio que sabe que serviços existem. |
| `backend/ia/lmstudio.py` | Faz o pedido ao modelo local no LM Studio, com o esquema JSON da resposta. Só aceita endereços do próprio computador. |
| `backend/ia/gemini.py` | Faz o pedido ao Gemini pela API REST, só com a biblioteca padrão do Python. A chave vai num cabeçalho, nunca no endereço. |
| `backend/ia/claude.py` | Faz o pedido ao Claude pelo pacote `anthropic`, com saída estruturada. |
| `backend/priorizacao/ia.py` | Monta o pedido (instruções, dados dos pedidos e esquema da resposta), valida a resposta e, se alguma coisa falhar, usa a regra local. |
| `backend/requisitos/gerar.py` | Propõe user stories a partir de um pedido aprovado (ecrã 10). Envia o título, a descrição, a categoria e o papel de quem pediu; sem IA, usa um modelo local que monta as frases a partir do pedido. |

Qualquer módulo que precise de IA faz o mesmo que a priorização: chama `pedir_json(instrucoes, dados, esquema)`, valida o que vem e tem uma alternativa local. A geração de user stories (ecrã 10) faz isto desde o Sprint 5.

## Qual serviço se usa

| Variável definida | Serviço |
|---|---|
| Nenhuma | Nenhum: regra local, sem rede e sem custos |
| `LMSTUDIO_URL` | Gemma 4 no LM Studio, no próprio computador (é o que usamos) |
| `GEMINI_API_KEY` | Gemini |
| `ANTHROPIC_API_KEY` | Claude |
| Várias | O local, depois o Gemini, depois o Claude. `IA_FORNECEDOR` obriga a um deles |

O modelo de cada serviço também se escolhe por variável: `LMSTUDIO_MODELO` (por omissão `google/gemma-4-e4b`), `GEMINI_MODELO` e `IA_MODELO` (por omissão `claude-opus-5-5`).

## Usar o Gemma 4 no LM Studio

Não precisa de chave e os dados não saem do computador ([D9](decisoes.md#d9-gemma-4-no-computador-com-o-lm-studio-23112026)).

1. Instalar o [LM Studio](https://lmstudio.ai) (no macOS, `brew install --cask lm-studio`) e abri-lo uma vez.
2. Descarregar o modelo (cerca de 7 GB): `~/.lmstudio/bin/lms get google/gemma-4-e4b`. É o mesmo Gemma 4 E4B que o Ollama tem como `gemma4`; escolhemos este tamanho porque cabe num computador com 16 GB.
3. Ligar o servidor, só no próprio computador: `~/.lmstudio/bin/lms server start --port 1234 --bind 127.0.0.1`.
4. No `.env` da raiz: `LMSTUDIO_URL=http://host.docker.internal:1234` (sem Docker, `http://localhost:1234`).
5. `docker compose up --build`, entrar como `ricardo` e pedir a sugestão. O post-it diz "Sugestão feita pelo Gemma 4 (local, no LM Studio)".

Num Mac M1 Pro com 16 GB, a primeira sugestão demorou 35 segundos (o modelo ainda não estava carregado) e as seguintes 4 a 7. Por isso o limite é de 60 segundos (`LMSTUDIO_TEMPO_LIMITE`). O servidor só aceita endereços locais em `LMSTUDIO_URL`.

## Segurança das chaves

- O modelo local não tem chave. Se se ligar a autenticação no LM Studio, o token vai em `LMSTUDIO_API_KEY`, no `.env`.
- As chaves só existem no `.env` da raiz, que o Git ignora e as imagens Docker não levam. Convém só o dono o poder ler: `chmod 600 .env`.
- Uma chave vai sempre num cabeçalho, nunca no endereço, e nunca aparece nas respostas da API nem nos registos.
- `config/tests/test_segredos.py` falha se alguma chave entrar num ficheiro que vai para o GitHub.
- Uma chave que tenha sido mostrada a alguém apaga-se no site do serviço e cria-se outra.

Para o Gemini usamos por omissão o `gemini-3.5-flash-lite`: é o modelo mais barato e o que tem mais pedidos por dia no plano gratuito (em novembro de 2026, cerca de 500 por dia, contra 20 do Gemini 3.8 Flash). Para sugerir uma ordem ou escrever user stories chega. Os limites gratuitos mudam com frequência e contam por projeto e por modelo; os números certos estão no Google AI Studio.

## Ligar o Gemini ou o Claude (opcional)

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

Nenhum teste chama um serviço a sério, nem o local. Os testes em `backend/ia/tests/` simulam a resposta do Gemini e verificam o endereço, o cabeçalho com a chave, o tempo limite e o que acontece com respostas cortadas ou que não são JSON. Os testes da priorização simulam o cliente e verificam que uma falha leva sempre à regra local.

## Ver também

- [Registo de decisões](decisoes.md)
- [Desenho de software](desenho.md)
- [Testes](../06-codigo/testes.md)
