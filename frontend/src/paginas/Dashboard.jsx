import { Link } from "react-router-dom";
import Cabecalho from "../componentes/Cabecalho.jsx";
import { AvisoExemplo, RELEASES } from "../exemplo.jsx";

const NUMEROS = [
  ["Submetidos", "128", "pedidos novos"],
  ["Aprovados", "41", "32% dos submetidos"],
  ["Rejeitados", "17", "com razão escrita"],
  ["Lead time", "12 dias", "do pedido à entrega"],
  ["Cycle time", "5 dias", "do início à entrega"],
];
const POR_RELEASE = [["Release 1.0", 6, "lancada"], ["Release 2.0", 9, "em_curso"], ["Release 3.0", 5, "planeada"]];
const PARADAS = [
  ["Aviso por email quando o pedido é lido", "Em revisão há 5 dias"],
  ["Filtrar por data de validade", "Em análise há 4 dias"],
];
const ESTADO_DA_RELEASE = { lancada: "lançada", em_curso: "atrasada 4 dias", planeada: "em planeamento" };

// Ecrã 14. Números já calculados, sem relatórios à mão (Helena). Sem horas nem commits.
export default function Dashboard() {
  const maior = Math.max(...POR_RELEASE.map(([, n]) => n));
  return (
    <section>
      <Cabecalho titulo="Dashboard" sub="últimos 3 meses · números de exemplo">
        <select className="filtro" aria-label="Período" defaultValue="3m" disabled><option value="3m">Período</option></select>
        <button className="secundario" disabled>Exportar</button>
      </Cabecalho>
      <AvisoExemplo />
      <dl className="painel numeros">
        {NUMEROS.map(([nome, valor, nota]) => (
          <div key={nome}><dt>{nome}</dt><dd>{valor}</dd><dd className="suave">{nota}</dd></div>
        ))}
      </dl>
      <div className="grelha-lado">
        <div className="painel">
          <h2 className="titulo-mao">Funcionalidades por release</h2>
          <div className="barras" role="img" aria-label="Release 1.0: 6, Release 2.0: 9, Release 3.0: 5">
            {POR_RELEASE.map(([nome, n, estado]) => (
              <div key={nome} className="barra-vertical">
                <strong>{n}</strong>
                <span className={`coluna-barra ${estado}`} style={{ height: `${(n / maior) * 100}%` }} />
                <span className="suave">{nome}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="coluna">
          <div className="painel">
            <h2 className="titulo-mao">Progresso do roadmap</h2>
            {RELEASES.map((r) => (
              <div key={r.nome} className="progresso">
                <div className="linha-cartao"><strong>{r.nome}</strong><span className="suave">{r.progresso}% · {ESTADO_DA_RELEASE[r.estado]}</span></div>
                <div className={`barra ${r.estado}`}><span style={{ width: `${r.progresso}%` }} /></div>
              </div>
            ))}
          </div>
          <div className="painel">
            <h2 className="titulo-mao">Paradas há mais de três dias</h2>
            <ul className="linhas">
              {PARADAS.map(([titulo, ha]) => <li key={titulo}><span>{titulo}</span><span className="suave">{ha}</span></li>)}
            </ul>
          </div>
        </div>
      </div>
      <p className="nota">Lead time conta desde o dia do pedido; cycle time desde que a funcionalidade entra Em desenvolvimento. As duas acabam em Concluído. <Link to="/dashboard/carga">Ver a carga das equipas</Link>.</p>
    </section>
  );
}
