import { Link } from "react-router-dom";
import Cabecalho from "../componentes/Cabecalho.jsx";
import { iniciais } from "../componentes/formatos.js";
import { AvisoExemplo, EQUIPAS } from "../exemplo.jsx";

const TIPOS = [["novo", "Novo"], ["manutencao", "Manutenção"], ["bugs", "Bugs"], ["administrativo", "Administrativo"]];
const total = (e) => TIPOS.reduce((soma, [chave]) => soma + e[chave], 0);

// Ecrã 15. Carga em pontos e por tipo de trabalho; passar a capacidade gera aviso (Helena).
export default function CargaEquipas() {
  const acima = EQUIPAS.filter((e) => total(e) > e.capacidade);
  const escala = Math.max(...EQUIPAS.map((e) => Math.max(total(e), e.capacidade))) * 1.05;
  return (
    <section>
      <Cabecalho titulo="Carga das equipas" sub="Sprint 4 · capacidade de 10 pontos por equipa">
        <select className="filtro" aria-label="Sprint" defaultValue="4" disabled><option value="4">Sprint 4</option></select>
      </Cabecalho>
      <AvisoExemplo />
      <div className="painel carga">
        {EQUIPAS.map((e) => {
          const t = total(e);
          return (
            <div key={e.nome} className="linha-carga">
              <strong>{e.nome}</strong>
              <span className="avatares">{e.pessoas.map((p) => <span key={p} className="avatar" title={p}>{iniciais(p)}</span>)}</span>
              <div className="pista-carga" aria-label={`${e.nome}: ${t} de ${e.capacidade} pontos`}>
                {TIPOS.map(([chave]) => (
                  <span key={chave} className={`tipo ${chave}`} style={{ width: `${(e[chave] / escala) * 100}%` }} />
                ))}
                <span className="capacidade" style={{ left: `${(e.capacidade / escala) * 100}%` }} />
              </div>
              <span className={t > e.capacidade ? "alerta" : undefined}>
                {t} / {e.capacidade}{t > e.capacidade && <> · <span>Acima da capacidade</span></>}
              </span>
            </div>
          );
        })}
        <ul className="legenda">
          {TIPOS.map(([chave, nome]) => <li key={chave}><span className={`tipo ${chave}`} />{nome}</li>)}
          <li><span className="capacidade-legenda" />capacidade</li>
        </ul>
      </div>
      <div className="painel tabela-painel">
        <table>
          <thead>
            <tr><th>Equipa</th>{TIPOS.map(([, nome]) => <th key={nome}>{nome}</th>)}<th>Total</th></tr>
          </thead>
          <tbody>
            {EQUIPAS.map((e) => (
              <tr key={e.nome}><td>{e.nome}</td>{TIPOS.map(([chave]) => <td key={chave}>{e[chave]}</td>)}<td>{total(e)} / {e.capacidade}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      {acima.length > 0 && (
        <div className="postit coral">
          <p>A {acima[0].nome} tem {total(acima[0])} pontos para {acima[0].capacidade}. Passa «Modo escuro» para a Equipa C?</p>
        </div>
      )}
      <div className="botoes">
        <button disabled>Reatribuir funcionalidades</button>
        <Link className="botao secundario" to="/equipa">Ver a Equipa A</Link>
      </div>
    </section>
  );
}
