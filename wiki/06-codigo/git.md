# Git e pull requests

[Índice](../README.md) · [← Testes](testes.md) · [Equipa e papéis →](../07-scrum/equipa-e-papeis.md)

- Há uma branch principal, a `main`.
- Cada cartão do Jira tem a sua branch: `feature/EDS-164-ambiente`.
- Cada pessoa faz commit do seu próprio trabalho, com a sua conta. É o histórico do Git que mostra quem fez o quê.
- Mensagens de commit no formato da secção [Mensagens de commit](#mensagens-de-commit), mais abaixo.
- O trabalho volta à `main` por pull request. Outra pessoa revê e aprova.
- O GitHub Actions tem de estar verde.
- Se a IA ajudou, diz-se no pull request para quê, e acrescenta-se uma linha ao registo de uso de IA (`docs/registo-ia/registo_uso_ia.tex`).
- Palavras-passe e chaves nunca entram no repositório.

A definição de concluído completa está no epic [EDS-158](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-158).

```bash
git switch main
git pull
git switch -c feature/EDS-167-submeter-pedido
```

## Mensagens de commit

Seguimos os [Conventional Commits](https://www.conventionalcommits.org/pt-br), sem emojis. Desde 14/11/2026 todos os commits usam este formato:

```text
tipo(âmbito): descrição
```

- **tipo:** diz a intenção do commit (`feat`, `fix`, `docs`...), da tabela abaixo.
- **(âmbito):** opcional, a parte do projeto que mudou, em minúsculas: `pedidos`, `contas`, `frontend`, `docker`, `wiki`, `readme`, `modelacao`, `registo-ia`.
- **descrição:** curta (até umas quatro ou cinco palavras), em português de Portugal, a dizer o que fizemos.
- **Rodapé:** opcional, a chave do cartão do Jira numa linha à parte, depois de uma linha em branco: `Refs: EDS-169`.

Um `!` depois do tipo ou do âmbito marca uma mudança que parte o que já existia: `feat(api)!: ...`.

Os commits de 28/10 a 14/11 ainda têm um emoji no início (`:sparkles:`, `:books:`...). Ficam assim, porque mudar o histórico já publicado obrigava a reescrevê-lo no GitHub.

| Tipo | Quando |
|---|---|
| `feat` | Funcionalidade nova ou aspeto da interface |
| `fix` | Correção de um erro |
| `docs` | Documentação: README, wiki, LaTeX, diagramas, comentários |
| `test` | Testes novos ou alterados |
| `build` | Dependências |
| `ci` | Docker e GitHub Actions |
| `chore` | Configuração, `.gitignore`, mover ficheiros |
| `refactor` | Reorganizar código sem mudar o que faz |
| `perf` | Desempenho |
| `revert` | Desfazer um commit anterior |

Exemplos:

```bash
git commit -m "feat(pedidos): aviso de pedidos parecidos" -m "Refs: EDS-169"
git commit -m "fix(contas): erro ao entrar sem email"
git commit -m "docs(wiki): casos de uso por ator"
git commit -m "ci(docker): postgresql no docker compose"
git commit -m "test(pedidos): voto repetido retira o voto"
```

Um commit faz uma coisa só. Se a mensagem precisa de "e" para juntar duas coisas diferentes, são dois commits.

## Versões

Cada sprint que entrega trabalho fecha com uma versão numerada ([EDS-184](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-184)). Assim sabe-se sempre o que foi apresentado em cada sprint e consegue-se voltar a esse ponto.

- **Numeração:** `v0.<sprint>.<correção>`. Fica em `0.x` até à entrega final, que é a `v1.0.0`. Uma correção a uma versão já apresentada sobe o último número (`v0.4.1`).
- **Quando:** na review do sprint, no último commit que a equipa apresentou.
- **Onde:** uma tag no Git e uma release no GitHub com o que entrou; a mesma versão no Jira, com os cartões do sprint ligados a ela.

```bash
git tag -a v0.4.0 -m "Sprint 4: segundo incremento"
git push origin v0.4.0
```

| Versão | Sprint | O que tem |
|---|---|---|
| `v0.3.0` | 3 | Arquitetura, modelação UML, wireframes corrigidos, base do back-end e do front-end, Docker e testes no GitHub Actions |
| `v0.4.0` | 4 | Segundo incremento: oito ecrãs ligados à API (priorização com IA, backlog e sprints, quadro, comentários e notificações), ruff e cobertura no CI, ecrãs com o aspeto dos mockups |

Para ver uma versão antiga: `git switch --detach v0.3.0` (e `git switch main` para voltar).

## Ver também

- [Testes](testes.md)
- [AGENTS.md](../../AGENTS.md)
