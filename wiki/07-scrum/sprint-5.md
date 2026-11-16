# Sprint 5

[Índice](../README.md) · [← Apresentação do Sprint 4](apresentacao-sprint-4.md) · [Apresentação final →](apresentacao-sprint-5.md)

De 17 de novembro a 11 de dezembro (quatro semanas, como diz o enunciado). É o último sprint e acaba na entrega final. Product Owner: Rui Machado. Scrum Master: Tiago Pereira.

## Objetivo

Entregar a versão `v1.0.0`: os sete ecrãs que ainda usam dados de exemplo (08 a 11 e 13 a 15) passam a falar com a API, e com eles ficam cobertas as sete áreas do enunciado. A edição e as versões dos pedidos, o refactoring, o deploy automático, o manual e a apresentação final fecham o projeto.

## O enunciado, ponto por ponto

Verificado a 16 de novembro contra o `SE_Project.pdf`. "Parte 1" e "parte 2" são as duas metades do trabalho de cada um neste sprint (ver [Como se divide o código](#como-se-divide-o-código)).

### Restrições

| O enunciado pede | Estado |
|---|---|
| Back-end e front-end, com frameworks modernos | Cumprido: Django REST Framework e React |
| Pode integrar serviços de terceiros (APIs) | Cumprido: Gemini ou Claude para a IA, opcionais ([IA no sistema](../04-arquitetura/ia.md)) |
| Pelo menos 8 interfaces além do CRUD e do login | Em curso: hoje há 7 ligadas à API (02 a 07 e 12); com a parte 1 ficam 11 (mais 08, 10, 13, 14); no fim, 14 |
| Estilo arquitetural justificado, com wireframes e mockups | Cumprido ([D1](../04-arquitetura/decisoes.md), Figma). Falta acertar os mockups dos ecrãs 08, 10, 13 e 14 com o que o código mostra agora (por exemplo, o 13 tem a conversa da equipa) |
| Tudo no Jira, com acesso para os docentes | Jira atualizado. **Por confirmar** que os dois docentes têm acesso ao site |
| Requisitos levantados com o Character.ai | Cumprido: cinco entrevistas ([EDS-55](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-55)) |
| Pelo menos uma ferramenta de IA para programar | Cumprido: Claude Code ([EDS-12](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-12)) e o Registo de Uso de IA |
| Rotação de Scrum Master e de Product Owner, documentada | Cumprido: contrato, [EDS-1](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-1), objetivo de cada sprint no Jira e [Equipa e papéis](equipa-e-papeis.md) |
| Presença de todos nas aulas | **Falta registar**: os cartões de presenças dos Sprints 3, 4 e 5 ([EDS-21](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-21) a [EDS-23](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-23)) estão vazios |

### Quadros do Jira

| O enunciado pede | Estado |
|---|---|
| Product Backlog, To Do, In Progress, Done | Cumprido: backlog e as colunas A fazer, Fazendo, Feito |
| Artifacts: links para wireframes, mockups, diagramas, GitHub e documentos | Cumprido: epic [EDS-2](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-2), com uma tabela de todos os artefactos (atualizada a 16/11) |
| SCRUM: provas de daily, planning, review e retrospetiva | **Falta**: só o Daily do Sprint 1 ([EDS-4](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-4)) tem registos. Os cartões de Planning, Review e Retrospetiva de todos os sprints estão com o modelo por preencher, alguns já marcados como Feito. Vale 15 % da nota (C1) |
| Team Contract | Cumprido: EDS-1, página no Confluence e `docs/contrato/`. Falta recompilar o PDF no Overleaf |

### Funcionalidades das sete áreas

| Área | Feito | Parte 1 | Parte 2 |
|---|---|---|---|
| Pedidos | Submeter, categorizar e etiquetar, pesquisar e filtrar | | Editar e ver versões ([EDS-186](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-186)) |
| Priorização | Ordem do Product Owner, votos, sugestão com IA, impacto e esforço | | |
| Product backlog | Product backlog, sprint backlog, estados, atribuir a equipas | | |
| Roadmap | | Roadmap visual e releases (ecrã 08) | Ecrã 09, milestones e dependências |
| Requisitos | | Gerar user stories com critérios (ecrã 10) | Rastreabilidade (ecrã 11) e marcar critérios cumpridos |
| Colaboração | Comentários, notificações, menções | Espaço de cada equipa (ecrã 13) | |
| Dashboards | | Submetidos, aprovados e rejeitados, por release, lead time, cycle time (ecrã 14) | Carga das equipas e progresso do roadmap (ecrã 15) |

### Metodologia e resultados

| O enunciado pede | Estado |
|---|---|
| Cinco sprints, o último de quatro semanas, apresentação oral em cada um | Cumprido |
| Personas, cenários e user stories | Cumprido |
| Protótipo (wireframes) | Cumprido |
| Arquitetura e desenho de software | Cumprido |
| Modelação: casos de uso, classes, atividades, sequência | Cumprido |
| Mockups | Cumprido (falta acertar os ecrãs novos, ver acima) |
| Programação e refactoring | Programação em curso; refactoring na parte 2 ([EDS-192](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-192)) |
| Testes, integração e entrega contínuas | Testes e integração contínua cumpridos; deploy automático por fazer ([EDS-196](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-196)) |

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
- [EDS-197](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-197): os diapositivos da apresentação final (5 minutos, 9 diapositivos) em `docs/sprint-5/apresentacao/`, com o que falta acontecer marcado a laranja.

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
