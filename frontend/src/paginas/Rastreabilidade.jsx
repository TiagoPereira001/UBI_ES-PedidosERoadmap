import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";
import { AvisoExemplo } from "../exemplo.jsx";

const ACONTECEU = [
  ["03/10", "Pedido criado", "Sofia Ferreira"],
  ["05/10", "Pedido aprovado", "Ricardo Almeida"],
  ["06/10", "US-31 aceite a partir do pedido", "Ricardo Almeida"],
  ["14/10", "PR #42 ligado à US-31", "Diogo Martins"],
];

// Ecrã 11. Do pedido chega-se ao código, e do pull request volta-se ao pedido (Helena).
export default function Rastreabilidade() {
  return (
    <section>
      <Cabecalho titulo="Rastreabilidade" sub="Exportar relatórios para Excel · do pedido à implementação">
        <span className="estado estado-em_desenvolvimento">Em desenvolvimento</span>
      </Cabecalho>
      <AvisoExemplo />
      <div className="cadeia">
        <div className="cartao elo">
          <h2 className="titulo-mao"><Icone nome="pedidos" /> Pedido</h2>
          <strong>Exportar relatórios para Excel</strong>
          <span className="suave">#201 · Sofia Ferreira · 14 votos</span>
        </div>
        <span className="seta-entre" aria-hidden="true"><Icone nome="seta" /></span>
        <div className="cartao elo">
          <h2 className="titulo-mao"><Icone nome="requisitos" /> User stories</h2>
          <strong>US-31 Exportar o relatório mensal</strong>
          <strong>US-32 Escolher as colunas</strong>
          <span className="suave">1 de 3 critérios cumpridos</span>
        </div>
        <span className="seta-entre" aria-hidden="true"><Icone nome="seta" /></span>
        <div className="cartao elo">
          <h2 className="titulo-mao"><Icone nome="codigo" /> Implementação</h2>
          <strong>Pull request #42</strong>
          <span className="suave">Diogo Martins · 3 commits · em revisão por Ana Sousa</span>
        </div>
      </div>
      <div className="painel">
        <h2 className="titulo-mao">O que aconteceu</h2>
        <table>
          <tbody>
            {ACONTECEU.map(([data, o, quem]) => (
              <tr key={o}><td className="suave">{data}</td><td>{o}</td><td className="suave">{quem}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
