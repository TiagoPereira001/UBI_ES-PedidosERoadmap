# Sprint 5

[Índice](../README.md) · [← Apresentação do Sprint 4](apresentacao-sprint-4.md) · [Apresentação final →](apresentacao-sprint-5.md)

De 17 de novembro a 11 de dezembro (quatro semanas, como diz o enunciado). É o último sprint e acaba na entrega final. Product Owner: Rui Machado. Scrum Master: Tiago Pereira.

## Objetivo

Entregar a versão `v1.0.0`: os sete ecrãs que ainda usam dados de exemplo (08 a 11 e 13 a 15) passam a falar com a API, e com eles ficam cobertas as sete áreas do enunciado. A edição e as versões dos pedidos, o refactoring, o deploy automático, o manual e a apresentação final fecham o projeto.

## O que o enunciado pede para o fim

| O enunciado | Onde fica |
|---|---|
| Pelo menos oito interfaces além do CRUD e do login | Hoje há sete ligadas (02 a 07 e 12). Com o Sprint 5 ficam catorze, todas além do login (01). |
| As sete áreas de funcionalidades | Faltam Roadmap (08, 09), Requisitos (10, 11), espaço de equipa (13) e Dashboards (14, 15), e a edição com versões nos Pedidos |
| "AI-assisted prioritization" e "automatic generation of User Stories" | A IA passa a estar numa pasta própria, `backend/ia/`, com Gemini e Claude, e serve as duas. Ver [IA no sistema](../04-arquitetura/ia.md) |
| "Continuous integration and deployment" | A integração contínua já existe; entra o deploy automático das imagens Docker |
| "Programming and Refactoring" | Um cartão só para refactoring, com o antes e o depois na wiki |
| Apresentação oral na última semana | Apresentação final em LaTeX (Beamer), com o projeto todo e o Sprint 5 |

## Sprint backlog

| Cartão | O quê | Pontos | Quem | Ecrãs |
|---|---|---|---|---|
| [EDS-185](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-185) | Ligar a IA ao Gemini, com a regra local como alternativa | 3 | Tiago | 05 |
| [EDS-186](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-186) | Editar pedidos e ver versões (US-03) | 5 | Tiago | 04 |
| [EDS-196](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-196) | Deploy automático depois dos testes | 5 | Tiago | |
| [EDS-198](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-198) | Entrega final e versão `v1.0.0` | 2 | Tiago | |
| [EDS-187](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-187) | Roadmap visual e releases (US-14, US-15) | 8 | Rui | 08, 09 |
| [EDS-188](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-188) | Milestones e dependências (US-16, US-17) | 5 | Rui | 08, 09 |
| [EDS-189](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-189) | Gerar user stories com critérios de aceitação (US-18) | 5 | Marcus | 10 |
| [EDS-190](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-190) | Rastreabilidade (US-19) | 5 | Marcus | 11 |
| [EDS-191](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-191) | Espaço de cada equipa (US-24) | 5 | João | 13 |
| [EDS-192](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-192) | Refactoring e revisão do código | 3 | João | |
| [EDS-193](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-193) | Manual de utilização | 3 | João | todos |
| [EDS-194](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-194) | Métricas do dashboard (US-25, US-26, US-27) | 5 | Felipe | 14 |
| [EDS-195](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-195) | Carga das equipas e progresso do roadmap (US-28, US-29) | 3 | Felipe | 15 |
| [EDS-197](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-197) | Apresentação final em LaTeX | 3 | Rui e Tiago | |

São 60 pontos em quatro semanas. A divisão é uma proposta para a Planning ([EDS-45](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-45)): se alguém trocar, muda-se o responsável no Jira.

## Como se divide o código

Como no Sprint 4, cada pessoa fica com um módulo inteiro, do servidor ao ecrã, com testes e a página da wiki.

| Quem | Módulo | Pasta no servidor | Ecrãs |
|---|---|---|---|
| Tiago | IA e Pedidos (edição e versões), deploy | `backend/ia/`, `backend/pedidos/`, `.github/workflows/` | 04, 05 |
| Rui | Roadmap | `backend/roadmap/` (novo) | 08, 09 |
| Marcus | Requisitos | `backend/requisitos/` (novo) | 10, 11 |
| João | Colaboração (espaço de equipa) e refactoring | `backend/colaboracao/` | 13 |
| Felipe | Métricas | `backend/metricas/` (novo) | 14, 15 |

A ordem dos commits importa outra vez, porque uns módulos usam os outros: Tiago (a IA, que os requisitos usam), Rui (o roadmap, que as métricas usam), Marcus, João e, no fim, Felipe.

Cada módulo novo segue o desenho que já existe ([desenho de software](../04-arquitetura/desenho.md)): `models.py`, `servicos.py` com as regras, `api.py` com os endpoints, `tests/` e o ecrã em `frontend/src/paginas/`. Um módulo não mexe nas tabelas de outro: pede-lhe os dados através dos serviços.

## Já feito no arranque (16/11)

- Sprint 4 fechado no Jira e Sprint 5 iniciado, com os cartões acima e a versão `v1.0.0` no Jira.
- [EDS-185](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-185): a pasta `backend/ia/` com o Gemini e o Claude atrás do mesmo cliente. Sem chave tudo continua com a regra local; com `GEMINI_API_KEY` usa o Gemini. O ecrã 05 diz que serviço fez a sugestão. Ainda não decidimos se vamos usar mesmo uma chave.
- [EDS-197](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-197): os diapositivos da apresentação final em `docs/sprint-5/apresentacao/`, com as partes do Sprint 5 por fechar no fim.

## Calendário

| Semana | O que deve estar pronto |
|---|---|
| 17 a 20 nov | Planning. IA e roadmap (Tiago, Rui) |
| 23 a 27 nov | Requisitos e espaço de equipa (Marcus, João). Ponto de situação a meio do sprint, como diz o contrato |
| 30 nov a 4 dez | Métricas (Felipe), edição de pedidos e deploy (Tiago), refactoring (João) |
| 7 a 11 dez | Manual, ensaio da apresentação, Review, Retrospetiva e `v1.0.0` a 11/12 |

## Cerimónias

Daily [EDS-44](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-44), Planning [EDS-45](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-45), Review [EDS-46](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-46), Retrospetiva [EDS-47](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-47), Presenças [EDS-23](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-23).

## Ver também

- [Apresentação final](apresentacao-sprint-5.md)
- [Sprint 4](sprint-4.md)
- [Sprints](sprints.md)
- [Estado atual](../currentstate.md)
