# Mockups

[Índice](../README.md) · [← Wireframes](wireframes.md) · [Arquitetura →](../04-arquitetura/arquitetura.md)

Os mockups mostram o aspeto final (cores, letra, texto real), ao contrário dos wireframes, que só mostram a estrutura.

Cartão: [EDS-163](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-163). Os mockups dos 15 ecrãs estão no [Figma](https://www.figma.com/design/VGH6pNIEVkvzY6QtVo8gcr), página **Alta Fidelidade**.

## O mundo visual

O quadro Scrum da equipa, em versão digital:

| Peça | Como é | No código (`frontend/src/estilo.css`) |
|---|---|---|
| Fundo | Parede cinzenta `#ECEDE8`, quadros brancos `#FBFBF8` | `--parede`, `--quadro` |
| Letra | Kalam nos títulos, Public Sans no resto | `--letra-mao`, `--letra` |
| Ação | Botão principal a tinta preta; secundário branco com contorno | `button`, `button.secundario` |
| Estados | Post-its com a cor de cada estado da US-12; Rejeitado sem cor, riscado | `.estado-*` |
| Votos | Autocolante coral | `.votos` |
| Etiquetas e cabeçalhos | Fita-cola `#E6DCC0` | `.etiqueta`, `.titulo-fita` |
| Fichas | Cartão branco com a linha vermelha por baixo do título | `.cartao` |
| IA | Post-it amarelo ao lado da decisão humana, nunca a decisão | `.postit` |
| Menu | Sete áreas com ícone; a área aberta num post-it amarelo, com os ecrãs dela por baixo | `.menu`, `.area.ativa` |

## O que mudou no Sprint 4

Os mockups foram acertados com o que o código faz, para os entregáveis baterem certo (critério C2 do enunciado):

- **05 Priorização:** o esforço passou de S, M e L para pontos (decisão D6); entrou o aviso de capacidade (US-06) e o post-it da IA com a razão de cada sugestão (US-08).
- **07 Quadro do sprint:** a coluna "Em curso" passou a "Em desenvolvimento", o nome do estado na US-12.

Desde o Sprint 4 ([EDS-181](https://ubi-team-ebw5rr6y.atlassian.net/browse/EDS-181)) os 15 ecrãs do front-end seguem os mockups: o mesmo menu, o título à mão com as ações à direita, e a mesma disposição de cada ecrã (tabela com o painel ao lado, colunas do quadro, fichas, post-its). O ecrã 01 ocupa a página toda, sem menu. Os ecrãs que ainda não estão ligados à API (08 a 11, 13 a 15) têm o mesmo aspeto, com dados de exemplo.

## Ainda por acertar

- **04 Detalhe do pedido:** o mockup mostra as versões do pedido (US-03) e "Gerar user stories" (US-18), que entram no Sprint 5.

## Ver também

- [Wireframes](wireframes.md)
