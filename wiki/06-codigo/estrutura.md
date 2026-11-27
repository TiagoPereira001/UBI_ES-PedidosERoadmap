# Estrutura do código

[Índice](../README.md) · [← Como correr o projeto](como-correr.md) · [Testes →](testes.md)

```
backend/
  config/            definições do Django e rotas principais
  contas/            módulo Contas: utilizador, papéis, entrar e registar
    models.py        Utilizador e Papel
    api.py           endpoints /api/contas/
  pedidos/           módulo Pedidos
    models.py        Pedido, Categoria, Etiqueta, Voto, MudancaEstado, Estado, Origem
    servicos.py      regras: criar, classificar, mudar estado (e quem pode), votar, procurar parecidos
    api.py           endpoints /api/pedidos/, /api/categorias/ e /api/etiquetas/
    tests/           testes das regras e da API
  priorizacao/       módulo Priorização
    models.py        Estimativa (impacto, esforço, lugar na ordem) e AlteracaoOrdem
    servicos.py      regras: estimar, ordenar, lista com o aviso de capacidade
    ia.py            sugestão de prioridade: pede à IA (pasta ia/) ou usa a regra local
    api.py           endpoints /api/priorizacao/
    tests/           testes das regras, da IA (sem a chamar) e da API
  ia/                ligação aos serviços de IA (Gemini e Claude); ver 04-arquitetura/ia.md
    cliente.py       escolhe o serviço pela chave que houver e devolve a resposta em JSON
    gemini.py        Gemini (Google), pela API REST
    claude.py        Claude (Anthropic), pelo pacote anthropic
    tests/           testes da escolha do serviço e do pedido ao Gemini (sem rede)
  backlog/           módulo Product backlog
    models.py        Equipa, Sprint, ItemBacklog
    servicos.py      regras: acrescentar ao backlog, criar, começar e fechar sprints, pôr no sprint, quadro, equipas
    api.py           endpoints /api/backlog/
    tests/           testes das regras e da API
  colaboracao/       módulo Colaboração
    models.py        Comentario, Notificacao, Preferencias, MembroEquipa e MensagemEquipa (espaço de cada equipa)
    servicos.py      regras: comentar, editar e apagar (só o autor), menções, quem segue um pedido, notificar;
                     no espaço da equipa, quem lá está, quem escreve na conversa e quem muda os membros
    sinais.py        avisa quem segue um pedido quando o estado muda
    api.py           endpoints /api/colaboracao/
    tests/           testes das regras e da API
  roadmap/           módulo Roadmap (Sprint 5)
    models.py        Release; Milestone (nome, data, release, pedidos); Dependencia (pedido → depende_de, única)
    servicos.py      releases; milestones (estado calculado); dependências sem ciclos (atomic + select_for_update); avisos
    api.py           endpoints /api/roadmap/
    tests/           testes das regras e da API (inclui N+1 nas listagens)
  requisitos/        módulo Requisitos (Sprint 5)
    models.py        UserStory, Criterio de aceitação e Ligacao (o commit onde a user story foi feita)
    gerar.py         propostas de user stories: pede à IA (pasta ia/) ou usa o modelo local
    servicos.py      regras: propor, aceitar e marcar critérios (Product Owner); ligar o código; o que falta em cada pedido
    api.py           endpoints /api/requisitos/
    tests/           testes das propostas (sem chamar a IA), das regras e da API
frontend/
  src/
    App.jsx          menu e rotas (mesma ordem dos wireframes)
    api.js           única porta para o servidor
    paginas/         um ficheiro por ecrã dos wireframes
    componentes/     peças usadas dentro dos ecrãs (por exemplo, a conversa do pedido)
    exemplo.jsx      dados de exemplo dos ecrãs que ainda não usam a API
    testes/          testes dos ecrãs
```

## Endpoints

| Método | Caminho | O quê | Quem |
|---|---|---|---|
| GET | `/api/contas/eu/` | Quem está autenticado | Todos |
| POST | `/api/contas/registar/` | Criar conta (fica cliente) | Todos |
| POST | `/api/contas/entrar/` e `/sair/` | Entrar e sair | Todos |
| GET | `/api/categorias/` | Categorias | Todos |
| GET | `/api/etiquetas/` | Etiquetas já usadas | Todos |
| GET | `/api/pedidos/?q=&estado=&categoria=&etiqueta=&meus=1&ordem=votos` | Lista com pesquisa e filtros; `meus=1` mostra só os pedidos de quem está autenticado | Todos |
| POST | `/api/pedidos/` | Criar pedido | Autenticados |
| GET | `/api/pedidos/parecidos/?q=` | Pedidos parecidos | Todos |
| GET | `/api/pedidos/<id>/` | Detalhe com histórico e `pode_mudar_para` (os estados a que o utilizador pode levar o pedido) | Todos |
| POST | `/api/pedidos/<id>/voto/` | Votar ou retirar o voto | Autenticados |
| POST | `/api/pedidos/<id>/estado/` | Mudar o estado | Depende da passagem (tabela `QUEM_PODE` em `servicos.py`) |
| PATCH | `/api/pedidos/<id>/classificar/` | Categoria e etiquetas (US-02) | Product manager e Product Owner |
| GET | `/api/priorizacao/?ordem=&capacidade=` | Pedidos a priorizar, pela ordem pedida (`manual`, `impacto`, `esforco`, `relacao`, `votos`), com o aviso de capacidade | Todos |
| PATCH | `/api/priorizacao/<id>/estimativa/` | Impacto e esforço (US-09) | Product Owner; o esforço também o programador |
| POST | `/api/priorizacao/ordem/` | Gravar a ordem com a razão (US-06) | Product Owner |
| GET | `/api/priorizacao/historico/` | Últimas mudanças de ordem | Todos |
| GET | `/api/priorizacao/sugestao/` | Sugestão de prioridade com razão (US-08) | Product Owner |
| GET | `/api/backlog/` | Product backlog pela ordem do Product Owner (US-10) | Todos |
| POST | `/api/backlog/` | Acrescentar um pedido aprovado ao backlog | Product Owner |
| GET | `/api/backlog/equipas/` | Equipas | Todos |
| PATCH | `/api/backlog/<pedido>/equipa/` | Atribuir a uma equipa (US-13) | Gestor de projeto e Product Owner |
| GET, POST | `/api/backlog/sprints/` | Sprints por fechar; criar sprint com datas, objetivo e capacidade (US-11) | Todos; criar só o Product Owner |
| GET | `/api/backlog/sprints/<id>/` | Sprint com os itens, os pontos e o aviso de capacidade | Todos |
| POST, DELETE | `/api/backlog/sprints/<id>/itens/` | Pôr um item no sprint (só com estimativa) ou tirá-lo | Product Owner |
| POST | `/api/backlog/sprints/<id>/comecar/` e `/fechar/` | Começar e fechar; ao fechar, o que não acabou volta ao backlog | Product Owner |
| GET | `/api/backlog/sprints/<id>/quadro/?equipa=` | Quadro do sprint, uma coluna por estado (ecrã 07) | Todos |
| GET, POST | `/api/colaboracao/pedidos/<id>/comentarios/` | Conversa de um pedido; comentar (US-21) | Ler: todos; comentar: autenticados |
| PATCH, DELETE | `/api/colaboracao/comentarios/<id>/` | Editar ou apagar um comentário | Só o autor |
| GET | `/api/colaboracao/pessoas/` | Nomes para as menções com @ (US-23) | Autenticados |
| GET | `/api/colaboracao/notificacoes/` | As minhas notificações e quantas estão por ler (US-22) | Autenticados |
| POST | `/api/colaboracao/notificacoes/lidas/` | Marcar como lidas (as dadas, ou todas) | Autenticados |
| GET, PUT | `/api/colaboracao/preferencias/` | O que cada um quer receber, e se também por email | Autenticados |
| GET, POST | `/api/roadmap/` | Todas as releases (com milestones); criar uma release (US-14, US-15) | Todos; criar só o product manager |
| GET | `/api/roadmap/releases/<id>/` | Uma release com pedidos, milestones, dependências e avisos (ecrã 09) | Todos |
| GET | `/api/colaboracao/equipas/<id>/` | Espaço da equipa: membros, trabalho por acabar, conversa, e se quem está autenticado pode escrever ou gerir (US-24) | Todos |
| POST | `/api/colaboracao/equipas/<id>/mensagens/` | Escrever na conversa da equipa | Membros e gestor de projeto |
| POST | `/api/colaboracao/equipas/<id>/membros/` | Juntar uma pessoa à equipa | Gestor de projeto |
| GET, POST | `/api/roadmap/` | Todas as releases, com estado, progresso e se estão em risco; criar uma release (US-14, US-15) | Todos; criar só o product manager |
| GET | `/api/roadmap/releases/<id>/` | Uma release com os pedidos | Todos |
| POST, DELETE | `/api/roadmap/releases/<id>/pedidos/` | Pôr um pedido aprovado na release, ou tirá-lo | Product manager |
| POST | `/api/roadmap/releases/<id>/lancar/` | Marcar como lançada (só com os pedidos todos concluídos) | Product manager |
| POST, PATCH, DELETE | `/api/roadmap/milestones/` | Criar, mudar e apagar milestones; pôr/tirar pedidos (US-16) | Product manager |
| POST, DELETE | `/api/roadmap/dependencias/` | Registar ou apagar dependência entre pedidos (US-17); recusa ciclos | Programador e product manager |
| GET | `/api/requisitos/pedidos/` | Pedidos aprovados de onde se geram user stories, com quantas já têm | Todos |
| GET, POST | `/api/requisitos/pedidos/<id>/historias/` | User stories aceites de um pedido, com os critérios; aceitar uma (US-18) | Todos; aceitar só o Product Owner |
| POST | `/api/requisitos/pedidos/<id>/propostas/` | Propostas de user stories, da IA ou do modelo local, e de onde vieram | Product Owner |
| GET | `/api/requisitos/rastreabilidade/` | Do pedido ao código e à release, com o que falta ligar (US-19) | Todos |
| POST | `/api/requisitos/historias/<id>/ligacoes/` | Ligar uma user story a um commit (só endereços https) | Programador e Product Owner |
| PATCH | `/api/requisitos/criterios/<id>/` | Marcar um critério de aceitação como cumprido | Product Owner |
| GET | `/api/metricas/?dias=30\|90\|365` | Números do dashboard: submetidos, aprovados, rejeitados, lead time e cycle time em dias, por mês, por release e pedidos parados há mais de três dias (US-25 a US-27) | Todos |

## Ecrãs

Os 15 ecrãs do Figma existem como página. Desde o Sprint 4, oito falam com a API: 01 Entrar, 02 Pedidos, 03 Novo pedido, 04 Detalhe do pedido (com a conversa), 05 Priorização, 06 Planear sprint, 07 Quadro do sprint e 12 Notificações. No Sprint 5 juntaram-se o 08 Roadmap, o 09 Release (`/roadmap/releases/:id`, com milestones e dependências), o 10 Gerar user stories, o 11 Rastreabilidade e o 13 Espaço da equipa. Os que ainda mostram dados de exemplo dizem isso no topo e ligam à API durante o Sprint 5.

## Ver também

- [Arquitetura](../04-arquitetura/arquitetura.md)
- [Wireframes](../03-prototipo/wireframes.md)
