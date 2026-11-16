# Apresentação final

[Índice](../README.md) · [← Sprint 5](sprint-5.md)

É a última apresentação e junta duas coisas: o projeto do princípio ao fim e o Sprint 5. Os diapositivos são em LaTeX (Beamer) e estão escritos na primeira pessoa do plural, como falamos na apresentação. O cartão é o [EDS-197](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-197).

## Onde estão os ficheiros

```
docs/sprint-5/apresentacao/
  apresentacao_final.tex   os diapositivos
  imagens/                 capturas da aplicação (ecra-*) e diagramas do FigJam (diagrama-*)
```

A pasta não depende de mais nada do repositório, por isso pode ir inteira para o Overleaf.

## Como compilar

1. Fazer um zip da pasta `docs/sprint-5/apresentacao/`.
2. No Overleaf: **New Project → Upload Project** e escolher o zip.
3. No menu do Overleaf: **Compiler: pdfLaTeX** e **Main document: apresentacao_final.tex**.
4. **Recompile**. O PDF fica em 16:9.

Não é preciso instalar nada: os pacotes usados (`beamer`, `tgheros`, `lmodern`, `tikz`, `booktabs`, `tabularx`) vêm com o Overleaf.

## O que está a laranja

Tudo o que ainda não aconteceu quando os diapositivos foram escritos (16/11) está dentro de `\atualizar{...}` e sai a laranja: os números finais, os módulos do Sprint 5 e as frases sobre o que esses módulos fazem. Antes de apresentar:

1. Confirmar cada frase a laranja. Se foi feito como está escrito, fica; se não, corrige-se o texto para dizer o que foi feito de verdade.
2. Atualizar os números (testes, cobertura, commits). Os comandos estão em [Testes](../06-codigo/testes.md); os commits contam-se com `git log --oneline | wc -l`.
3. Trocar as capturas marcadas com `% ATUALIZAR` pelas dos ecrãs 08, 10, 11, 14 e 15 já ligados à API.
4. Preencher as linhas do refactoring (EDS-192) e a reflexão da Retrospetiva (EDS-47).
5. No fim, na linha `\newcommand{\atualizar}...`, trocar `laranja` por `tinta`, para sair tudo a preto.

## Ordem e quem fala

O nome de quem fala aparece no rodapé de cada diapositivo (`\fala{...}` no `.tex`). Cada um explica o módulo que fez, porque a participação individual conta (C2).

| # | Parte | Quem | O que dizer |
|---|---|---|---|
| 1 | Abertura e o que vamos mostrar | Rui | O título e as duas partes |
| 2 | O problema e o produto | Rui | Folhas de cálculo e emails dão pedidos repetidos e prioridades sem razão; o que o sistema resolve |
| 3 | Equipa e rotação de papéis | Rui | A tabela dos cinco sprints |
| 4 | Como trabalhámos | Tiago | Scrum, Jira, contrato, GitHub com uma só branch |
| 5 | Requisitos | Rui | Entrevistas no Character.ai, 5 personas, 6 cenários, 29 user stories |
| 6 | Protótipo | Rui | Wireframes, mockups e o front-end igual aos mockups |
| 7 | Arquitetura | Tiago | Monólito modular e porque não microserviços |
| 8 | Modelação | Tiago | Casos de uso por ator, sequência, estados |
| 9 | Código | Tiago | Um módulo por pessoa, regras nos serviços |
| 10 | Qualidade e versões | Tiago | GitHub Actions, cobertura, versões por sprint |
| 11 | IA | Tiago | Character.ai, Claude Code, IA no produto, registo |
| 12 | Objetivo do Sprint 5 | Rui | Os sete ecrãs que faltavam e quem fez o quê |
| 13 | A IA atrás de um só cliente | Tiago | Gemini ou Claude, regra local sem chave |
| 14 | Pedidos | Tiago | Aviso de parecidos, histórico, edição com versões |
| 15 | Priorizar | Marcus | Impacto, esforço, ordem com razão, sugestão |
| 16 | Backlog, sprint e roadmap | Rui | Quadro do sprint e roadmap |
| 17 | Gerar user stories | Marcus | Proposta, revisão do Product Owner, rastreabilidade |
| 18 | Colaborar | João | Comentários, menções, avisos, espaço de equipa |
| 19 | Métricas | Felipe | Aprovados e rejeitados, lead time, cycle time, carga |
| 20 | Refactoring | João | Antes, depois e porquê |
| 21 | Deploy | Tiago | Do commit à versão publicada |
| 22 | O enunciado ponto por ponto | Rui | A tabela |
| 23 | O que aprendemos | Tiago | O que correu mal, o que correu bem, a retrospetiva |
| 24 | Perguntas | Todos | |

## Demonstração

Antes de começar: `docker compose down -v` e depois `docker compose up --build`, para os dados de exemplo virem limpos. As contas são as de sempre (nome + 123).

1. `sofia`: escrever um pedido parecido com um que já existe e ver o aviso; votar.
2. `marta`: passar o pedido a Em análise e aprovar.
3. `ricardo`: estimar, ordenar e pedir a sugestão da IA; acrescentar ao backlog, planear e começar o sprint.
4. `diogo`: mover no quadro e comentar com @sofia; voltar a `sofia` e ver a notificação.
5. Os ecrãs do Sprint 5 (roadmap, gerar user stories, rastreabilidade, espaço de equipa, dashboard), cada um mostrado por quem o fez.

## Perguntas que podem fazer

- **Porque um monólito e não microserviços?** Somos cinco, temos um só deploy e as fronteiras entre módulos chegam. Ver [D1](../04-arquitetura/decisoes.md).
- **E se a IA falhar ou não houver chave?** A regra local faz a sugestão e o ecrã diz isso. Ver [IA no sistema](../04-arquitetura/ia.md).
- **Como sabem que o código funciona?** Os testes correm em cada push e o GitHub Actions falha se a cobertura descer dos 90 %.
- **Quem fez o quê?** Está no Jira (responsável de cada cartão) e no GitHub (autor de cada commit).
- **Como usaram a IA a programar?** Com o Claude Code, sempre revisto por quem fez o commit, e registado no Registo de Uso de IA.

## Ver também

- [Sprint 5](sprint-5.md)
- [Apresentação do Sprint 4](apresentacao-sprint-4.md)
