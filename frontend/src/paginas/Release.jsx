import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";
import { AvisoExemplo } from "../exemplo.jsx";

const FUNCIONALIDADES = [
  { titulo: "Exportar relatórios para Excel", estado: "em_desenvolvimento", nome: "Em desenvolvimento", meta: "depende de: Filtros avançados na pesquisa" },
  { titulo: "Filtros avançados na pesquisa", estado: "aprovado", nome: "Aprovado", meta: "sem data ainda · Equipa A" },
  { titulo: "Modo escuro", estado: "aprovado", nome: "Aprovado", meta: "sem dependências · Equipa B" },
];
const MILESTONES = [["Beta para clientes", "15/11"], ["Lançamento", "30/11"]];

// Ecrã 09. Funcionalidades da release e dependências (Marta e Diogo).
export default function Release() {
  return (
    <section>
      <Cabecalho titulo="Release 2.0" sub="data prevista: 30/11 · 3 funcionalidades · 45% feito">
        <button className="secundario" disabled>Editar release</button>
        <button disabled>Adicionar funcionalidade</button>
      </Cabecalho>
      <AvisoExemplo />
      <div className="grelha-lado">
        <div className="painel">
          <h2 className="titulo-fita">Funcionalidades <span className="conta">{FUNCIONALIDADES.length}</span></h2>
          <ul className="cartoes">
            {FUNCIONALIDADES.map((f) => (
              <li key={f.titulo} className="cartao">
                <div className="linha-cartao"><span className="titulo-cartao">{f.titulo}</span><span className={`estado estado-${f.estado}`}>{f.nome}</span></div>
                <div className="meta-cartao">{f.meta}</div>
              </li>
            ))}
          </ul>
          <div className="postit coral">
            <p>Exportar relatórios depende de Filtros avançados, que ainda não tem data. Agenda-a antes de 30/11.</p>
          </div>
          <button className="secundario" disabled>Adicionar dependência</button>
        </div>
        <aside className="painel">
          <h2 className="titulo-fita">Milestones <span className="conta">{MILESTONES.length}</span></h2>
          <ul className="linhas">
            {MILESTONES.map(([nome, data]) => (
              <li key={nome}><Icone nome="bandeira" tamanho={18} /><span>{nome}</span><span className="suave">{data}</span></li>
            ))}
          </ul>
          <button className="secundario" disabled>Novo milestone</button>
        </aside>
      </div>
    </section>
  );
}
