import { Link } from "react-router-dom";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";
import { AvisoExemplo, DIAS_NO_ROADMAP, MESES, RELEASES } from "../exemplo.jsx";

const pos = (dia) => `${(dia / DIAS_NO_ROADMAP) * 100}%`;

// Ecrã 08. Releases como fitas ao longo dos meses. A que a equipa está a fazer leva fita amarela;
// a que está em risco e a entrega contratual ficam marcadas (Helena).
export default function Roadmap() {
  const hoje = Math.round((Date.now() - new Date(2026, 9, 1)) / 864e5);
  const mostrarHoje = hoje >= 0 && hoje <= DIAS_NO_ROADMAP;
  return (
    <section>
      <Cabecalho titulo="Roadmap" sub="outubro de 2026 a janeiro de 2027">
        <select className="filtro" aria-label="Período" defaultValue="trimestre" disabled>
          <option value="trimestre">Trimestre</option>
        </select>
        <button disabled>Nova release</button>
      </Cabecalho>
      <AvisoExemplo />
      <div className="painel roadmap">
        <div className="roadmap-meses">
          <span />
          {MESES.map((m) => <span key={m} className="titulo-mao">{m}</span>)}
        </div>
        <div className="roadmap-corpo">
          {RELEASES.map((r) => (
            <div key={r.nome} className="roadmap-linha">
              <div className="roadmap-nome">
                <strong>{r.nome}</strong>
                {r.emRisco && <span className="autocolante risco">Em risco</span>}
                {r.contrato && <span className="nota">Entrega contratual</span>}
              </div>
              <div className="roadmap-pista">
                <Link to="/roadmap/release" className={`fita-release ${r.estado}`} style={{ left: pos(r.inicio), width: pos(r.fim - r.inicio) }}>
                  {r.tema}
                </Link>
                {r.marco && (
                  <span className="marco" style={{ left: pos(r.diaMarco) }}><Icone nome="bandeira" tamanho={16} />{r.marco}</span>
                )}
              </div>
            </div>
          ))}
          {mostrarHoje && <span className="linha-hoje" style={{ left: `calc(var(--coluna-nomes) + (100% - var(--coluna-nomes)) * ${hoje / DIAS_NO_ROADMAP})` }}><em>hoje</em></span>}
        </div>
      </div>
      <p className="nota">Release 2.0 destacada: é a que a equipa está a fazer, e está em risco porque depende de «Filtros avançados». O detalhe abre ao clicar na fita.</p>
    </section>
  );
}
