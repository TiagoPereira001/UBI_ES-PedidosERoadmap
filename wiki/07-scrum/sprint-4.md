# Sprint 4

[Índice](../README.md) · [← Apresentação do Sprint 3](apresentacao-sprint-3.md) · [Apresentação do Sprint 4 →](apresentacao-sprint-4.md)

De 2 a 16 de novembro; a apresentação é na segunda-feira, 16 de novembro. Product Owner: Marcus Fernandes. Scrum Master: Felipe Fogaça.

## Objetivo

Segundo incremento: priorizar, planear e colaborar dentro do sistema. No fim do sprint, oito ecrãs falam com a API (01 Entrar, 02 Pedidos, 03 Novo pedido, 04 Detalhe, 05 Priorização, 06 Planear sprint, 07 Quadro do sprint e 12 Notificações). Tirando o 01 (entrada), são sete ecrãs com mais do que o login e o CRUD: pesquisa e filtros, aviso de pedidos parecidos, histórico de estados e conversa, priorização com IA, planeamento com capacidade, quadro e notificações. Os outros sete ecrãs (08 a 11 e 13 a 15) já estão no código com dados de exemplo e ligam à API no Sprint 5, para a entrega final passar as oito interfaces que o enunciado pede. Também entram a qualidade do código no CI, o desenho de software e o aspeto dos mockups no front-end.

O plano segue a ordem das aulas: construção e qualidade do código, revisões e refactoring, testes e integração contínua.

## O que o professor pediu no fim do Sprint 3

| Pedido | Onde está |
|---|---|
| Gestão de versões | Uma versão por sprint: tag no Git e release no GitHub (`v0.3.0`, `v0.4.0`) e a mesma versão no Jira, com os cartões ligados. Commits no formato `tipo(âmbito): descrição`, cada um com a sua conta. Ver [Git e versões](../06-codigo/git.md#versões) ([EDS-184](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-184)). |
| Automação dos testes | O GitHub Actions corre em cada push o ruff, os testes do servidor com cobertura mínima de 90 % e os testes e a build do front-end ([EDS-165](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-165), [EDS-182](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-182)). Ver [Testes](../06-codigo/testes.md). |
| Desenvolver o protótipo | Oito ecrãs ligados à API, com três módulos novos no servidor (priorização, backlog e colaboração) e os 15 ecrãs com o aspeto dos mockups. |

## Sprint backlog

| Cartão | O quê | Pontos | Quem |
|---|---|---|---|
| [EDS-174](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-174) | Etiquetas e quem muda cada estado (US-02, US-12) | 3 | Tiago |
| [EDS-182](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-182) | Qualidade do código no CI: ruff e cobertura | 2 | Tiago |
| [EDS-175](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-175) | Priorização: impacto, esforço e ordem (US-06, US-09) | 8 | Marcus |
| [EDS-176](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-176) | Sugestão de prioridade com IA (US-08) | 5 | Marcus |
| [EDS-177](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-177) | Product backlog e planeamento do sprint (US-10, US-11) | 8 | Rui |
| [EDS-178](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-178) | Quadro do sprint e equipas (US-12, US-13) | 5 | Rui |
| [EDS-161](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-161) | Desenho de software | 5 | Rui |
| [EDS-179](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-179) | Comentários e menções (US-21, US-23) | 5 | João |
| [EDS-180](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-180) | Notificações (US-22) | 5 | João |
| [EDS-181](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-181) | Aspeto dos mockups no front-end | 3 | Felipe |
| [EDS-163](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-163) | Mockups acertados com o código | 3 | Felipe |
| [EDS-183](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-183) | Apresentação oral | 2 | Marcus e Felipe |
| [EDS-184](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-184) | Gestão de versões: tags, releases e versões no Jira | 2 | Tiago |

São 56 pontos. Os cartões do primeiro incremento ([EDS-166](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-166) a [EDS-171](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-171)) já tinham a base feita no Sprint 3; o que lhes faltava entra no EDS-174 e no EDS-179.

## Como se divide o código

Cada pessoa fica com um módulo inteiro, do servidor ao ecrã, com os testes e a página da wiki. Assim cada um consegue explicar a sua parte na apresentação.

| Quem | Módulo | Ecrãs |
|---|---|---|
| Tiago | `pedidos` (etiquetas, estados por papel) e o CI | 02, 04 |
| Marcus | `priorizacao` (com a IA) | 05 |
| Rui | `backlog` e o desenho de software | 06, 07 |
| João | `colaboracao` | 04 (conversa), 12 |
| Felipe | Aspeto dos mockups e mockups no Figma | todos |

A ordem dos commits importa, porque cada módulo usa o anterior: Tiago, Marcus, Rui, João e Felipe.

## Cerimónias

Daily [EDS-40](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-40), Planning [EDS-41](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-41), Review [EDS-42](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-42), Retrospetiva [EDS-43](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-43), Presenças [EDS-22](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-22).

## Ver também

- [Apresentação do Sprint 4](apresentacao-sprint-4.md)
- [Sprints](sprints.md)
- [Estado atual](../currentstate.md)
