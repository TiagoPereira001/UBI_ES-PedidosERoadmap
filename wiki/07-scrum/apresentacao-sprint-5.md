# Apresentação final

[Índice](../README.md) · [← Sprint 5](sprint-5.md)

Cinco minutos, com o projeto do princípio ao fim e o Sprint 5. Os diapositivos são em LaTeX (Beamer), na primeira pessoa do plural, como falamos. O cartão é o [EDS-197](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-197).

## Onde estão os ficheiros

```
docs/sprint-5/apresentacao/
  apresentacao_final.tex   os 9 diapositivos
  imagens/                 4 capturas da aplicação (ecra-*) e o diagrama da arquitetura
```

A pasta não depende de mais nada do repositório, por isso pode ir inteira para o Overleaf.

## Como compilar

1. Fazer um zip da pasta `docs/sprint-5/apresentacao/`.
2. No Overleaf: **New Project → Upload Project** e escolher o zip.
3. No menu do Overleaf: **Compiler: pdfLaTeX** e **Main document: apresentacao_final.tex**.
4. **Recompile**. O PDF fica em 16:9.

Os pacotes usados (`beamer`, `tgheros`, `lmodern`, `booktabs`, `tabularx`) vêm com o Overleaf.

## Os 5 minutos

O rodapé de cada diapositivo diz quem fala e quanto tempo tem. Falam o Product Owner (Rui) e o Scrum Master (Tiago), como nas outras apresentações; os outros três estão lá para responder sobre o módulo que fizeram.

| # | Diapositivo | Quem | Tempo | A ideia a passar |
|---|---|---|---|---|
| 1 | Título | Rui | 10 s | O nome do sistema e a equipa |
| 2 | O problema e o que fizemos | Rui | 30 s | Pedidos espalhados por emails e folhas de cálculo; o sistema junta tudo |
| 3 | Como trabalhámos | Rui | 40 s | Cinco sprints, papéis rodados, Jira, Character.ai |
| 4 | Dos requisitos ao protótipo | Rui | 30 s | Personas, wireframes, mockups e modelação a bater certo |
| 5 | Arquitetura | Tiago | 45 s | Monólito modular, porque não microserviços, a IA com alternativa local |
| 6 | O sistema | Tiago | 50 s | Quatro ecrãs: priorização, quadro, roadmap, dashboard |
| 7 | O Sprint 5 | Rui | 40 s | O objetivo, quantos ecrãs, quem fez o quê |
| 8 | Qualidade e versões | Tiago | 30 s | Testes automáticos, cobertura, uma versão por sprint |
| 9 | O que aprendemos e perguntas | Tiago | 30 s | O que correu mal e bem, honestamente |

Somam 5 minutos e 5 segundos. Para caber, a demonstração ao vivo não entra: as capturas do diapositivo 6 fazem esse papel. Se o professor pedir para ver, tem-se a aplicação já aberta (`docker compose up --build` antes de começar) com a conta `ricardo`.

## O que está a laranja

O que ainda não tinha acontecido quando os diapositivos foram escritos está dentro de `\atualizar{...}` e sai a laranja. Antes de apresentar:

1. Confirmar cada frase a laranja; se não foi feito como está escrito, corrigir o texto.
2. Pôr os números finais: pontos feitos no Sprint 5 (diapositivo 7), testes e cobertura (diapositivo 8). Os testes contam-se com os comandos em [Testes](../06-codigo/testes.md).
3. Se o ecrã mudou, trocar as capturas em `imagens/`.
4. No fim, na linha `\newcommand{\atualizar}...`, trocar `laranja` por `tinta`, para sair tudo a preto.

## Perguntas que podem fazer

- **Porque um monólito e não microserviços?** Somos cinco, temos um só deploy e as fronteiras entre módulos chegam. Ver [D1](../04-arquitetura/decisoes.md).
- **E se a IA falhar ou não houver chave?** A regra local faz a sugestão e o ecrã diz isso. Ver [IA no sistema](../04-arquitetura/ia.md).
- **Como sabem que o código funciona?** Os testes correm em cada push e o GitHub Actions falha se a cobertura descer dos 90 %.
- **Quem fez o quê?** Está no Jira (responsável de cada cartão) e no GitHub (autor de cada commit).
- **Onde estão os registos das cerimónias?** No epic EDS-3 do Jira, um cartão por cerimónia e por sprint.

## Ver também

- [Sprint 5](sprint-5.md), com a verificação do enunciado ponto por ponto
- [Apresentação do Sprint 4](apresentacao-sprint-4.md)
