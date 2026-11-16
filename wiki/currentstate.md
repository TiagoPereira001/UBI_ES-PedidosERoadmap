# Estado atual

[Índice](README.md) · [Visão do produto →](01-produto/visao.md)

Última atualização: 16 de novembro de 2026, início do Sprint 5.

Esta página diz onde o projeto está. Quem mexe no projeto (pessoa ou agente de IA) atualiza-a quando alguma coisa muda.

## Sprint em curso

**Sprint 5**, de 17 de novembro a 11 de dezembro (quatro semanas, acaba na entrega final). Product Owner: Rui Machado. Scrum Master: Tiago Pereira. Ver [Sprint 5](07-scrum/sprint-5.md).

Objetivo: a versão `v1.0.0`. Os sete ecrãs que ainda usam dados de exemplo (08 a 11 e 13 a 15) passam a falar com a API: roadmap e releases, geração de user stories e rastreabilidade, espaço de equipa e métricas. Entram também a edição com versões dos pedidos, a IA com o Gemini, o refactoring, o deploy automático, o manual e a [apresentação final](07-scrum/apresentacao-sprint-5.md) em LaTeX.

O Sprint 4 fechou a 16 de novembro com a apresentação e a versão `v0.4.0`.

## Feito

- Personas, cenários e 29 user stories no Jira, revistos com as entrevistas no Character.ai. Ver [personas](01-produto/personas.md).
- Wireframes de baixa fidelidade dos 15 ecrãs no Figma, corrigidos a 23/10 com o que faltava das personas. Ver [wireframes](03-prototipo/wireframes.md).
- Diagramas para o Sprint 3 no FigJam: arquitetura, casos de uso, duas sequências, estados, atividades e modelo de dados. Fontes em `docs/sprint-3/modelacao/`. Ver [modelação](05-modelacao/casos-de-uso.md).
- Casos de uso com um diagrama por ator (Sofia, Marta, Ricardo, Diogo e Helena) e diagrama de classes com uma vista por persona, a 26/10, a pedido do professor. Ver [casos de uso](05-modelacao/casos-de-uso.md) e [classes](05-modelacao/classes.md).
- Wireframes exportados em imagem para `docs/sprint-3/wireframes/`.
- Documento de requisitos não funcionais em LaTeX: `docs/sprint-3/requisitos_nao_funcionais.tex`.
- Base do código: back-end Django com contas e pedidos, front-end React com os 15 ecrãs e um estilo simples.
- Docker: `docker compose up --build` levanta o projeto inteiro (PostgreSQL, back-end e front-end) na mesma rede, com o código a recarregar sozinho. Ver [como correr](06-codigo/como-correr.md).
- Testes automáticos: 99 no back-end e 42 no front-end, todos a passar (também no PostgreSQL, dentro do Docker). Ver [testes](06-codigo/testes.md).
- Integração contínua (`.github/workflows/ci.yml`) a correr no GitHub em cada push e pull request, com ruff e cobertura mínima de 90 % no back-end.
- Sprint 4: oito ecrãs ligados à API (01 a 07 e 12). Etiquetas e estados por papel, priorização com impacto, esforço e sugestão de IA, product backlog, sprints e quadro com equipas, comentários, menções e notificações. Ver [estrutura do código](06-codigo/estrutura.md) e [desenho de software](04-arquitetura/desenho.md).
- O front-end tem o aspeto dos [mockups](03-prototipo/mockups.md), e os mockups 05 e 07 foram acertados com o código.
- Sprint 5, no arranque: a ligação à IA passou para `backend/ia/`, com o Gemini e o Claude atrás do mesmo cliente e a regra local quando não há chave. Ver [IA no sistema](04-arquitetura/ia.md). Os diapositivos da apresentação final estão em `docs/sprint-5/apresentacao/`.

## Por fazer

- Registos das cerimónias que ficaram vazios: Sprint 3 ([EDS-36](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-36) a [EDS-39](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-39), [EDS-21](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-21)) e Sprint 4 ([EDS-40](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-40) a [EDS-43](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-43), [EDS-22](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-22)). Quem esteve escreve o que se passou.
- Recompilar o PDF do contrato no Overleaf e anexá-lo ao [EDS-1](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-1).
- Compilar no Overleaf o documento de requisitos não funcionais (`docs/sprint-3/requisitos_nao_funcionais.tex`, [EDS-159](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-159)).
- A arquitetura está na wiki ([arquitetura](04-arquitetura/arquitetura.md)), mas ainda não há um documento em LaTeX em `docs/` ([EDS-153](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-153)).
- Proteger a `main` no GitHub (só o Tiago tem permissões).
- O resto está no [Sprint 5](07-scrum/sprint-5.md).

## Decisões em aberto

- Se usamos uma chave do Gemini na apresentação final. Sem chave, a sugestão usa a regra local e tudo funciona na mesma ([D8](04-arquitetura/decisoes.md#d8-gemini-e-claude-atrás-do-mesmo-cliente-16112026)).

## Onde está cada coisa

| O quê | Onde |
|---|---|
| Trabalho do dia a dia | [Jira, projeto EDS](https://ubi-team-ebw5rr6y.atlassian.net/jira/software/projects/EDS/boards/3) |
| Wireframes | [Figma](https://www.figma.com/design/VGH6pNIEVkvzY6QtVo8gcr), página Baixa Fidelidade |
| Diagramas | [FigJam](https://www.figma.com/board/czxBO7U14mX4uEDGr29P41) |
| Documentos entregues (PDF, LaTeX) | `docs/` |
| Código | `backend/` e `frontend/` |
| Esta documentação | `wiki/` |

## Ver também

- [Índice da wiki](README.md)
- [Sprint 5](07-scrum/sprint-5.md)
- [AGENTS.md](../AGENTS.md)
