import { useState } from "react";
import Cabecalho from "../componentes/Cabecalho.jsx";
import { AvisoExemplo } from "../exemplo.jsx";

const PROPOSTAS = [
  { id: 1, texto: "Como product manager, quero exportar o relatório mensal para Excel, para o enviar à direção." },
  { id: 2, texto: "Como cliente, quero escolher as colunas a exportar, para levar só o que preciso." },
  { id: 3, texto: "Como gestor de projeto, quero agendar a exportação, para a receber sem ter de pedir." },
];
const CRITERIOS = ["O ficheiro abre no Excel sem erros", "Os totais batem com o ecrã", "O nome do ficheiro tem o mês"];

// Ecrã 10. As histórias geradas são propostas: só entram no backlog as que o Product Owner aceitar (Ricardo).
export default function GerarHistorias() {
  const [estado, setEstado] = useState({ 1: "aceite" });
  const [feitos, setFeitos] = useState([true, false, false]);
  const visiveis = PROPOSTAS.filter((p) => estado[p.id] !== "rejeitada");
  const aceites = Object.values(estado).filter((e) => e === "aceite").length;

  return (
    <section>
      <Cabecalho titulo="User stories do pedido" sub={`«Exportar relatórios para Excel» · ${PROPOSTAS.length} propostas geradas · ${aceites} aceite${aceites === 1 ? "" : "s"}`}>
        <button className="secundario" disabled>Gerar de novo</button>
        <button disabled>Enviar aceites para o backlog</button>
      </Cabecalho>
      <AvisoExemplo />
      <div className="tres-colunas">
        <div className="cartao origem">
          <span className="rotulo">Pedido de origem</span>
          <strong>Exportar relatórios para Excel</strong>
          <p>Os relatórios só se veem no ecrã. Precisamos de os exportar para Excel para a direção, com totais por mês e por cliente.</p>
          <div className="meta-pedido"><span className="votos">14</span><span className="estado estado-aprovado">Aprovado</span></div>
        </div>
        <ul className="historias">
          {visiveis.map((p) => (
            <li key={p.id} className="cartao">
              <p>{p.texto}</p>
              {estado[p.id] === "aceite" ? (
                <div className="meta-pedido"><span className="estado estado-concluido">Aceite</span><span className="suave">aceite pelo Product Owner</span></div>
              ) : (
                <div className="botoes">
                  <button className="pequeno" onClick={() => setEstado({ ...estado, [p.id]: "aceite" })}>Aceitar</button>
                  <button className="secundario pequeno" disabled>Editar</button>
                  <button className="secundario pequeno" onClick={() => setEstado({ ...estado, [p.id]: "rejeitada" })}>Rejeitar</button>
                </div>
              )}
            </li>
          ))}
        </ul>
        <div className="painel">
          <h2 className="titulo-mao">Critérios de aceitação</h2>
          <p className="nota">da história aceite</p>
          {CRITERIOS.map((c, i) => (
            <label key={c} className="opcao">
              <input type="checkbox" checked={feitos[i]} onChange={() => setFeitos(feitos.map((f, j) => (j === i ? !f : f)))} />
              {c}
            </label>
          ))}
        </div>
      </div>
    </section>
  );
}
