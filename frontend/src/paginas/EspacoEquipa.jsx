import Cabecalho from "../componentes/Cabecalho.jsx";
import { iniciais } from "../componentes/formatos.js";
import { AvisoExemplo } from "../exemplo.jsx";

const PESSOAS = [
  ["Diogo Martins", "programador"],
  ["Ana Sousa", "programadora"],
  ["Ricardo Almeida", "Product Owner"],
  ["Helena Costa", "gestora de projeto"],
];
const TRABALHO = [
  ["Exportar relatórios para Excel", "em_desenvolvimento", "Em desenvolvimento", "Diogo Martins"],
  ["Filtros avançados na pesquisa", "em_desenvolvimento", "Em desenvolvimento", "Ana Sousa"],
  ["Votação nos pedidos", "concluido", "Concluído", "Diogo Martins"],
];
const SEGUIMOS = [
  ["Exportar relatórios para Excel", "em_analise", "Em análise", 14],
  ["Filtros avançados na pesquisa", "aprovado", "Aprovado", 7],
];

// Ecrã 13. Cada equipa vê o seu espaço: quem é, o que está a fazer e os pedidos que segue (US-24).
export default function EspacoEquipa() {
  return (
    <section>
      <Cabecalho titulo="Equipa A" sub="4 pessoas · 3 funcionalidades neste sprint">
        <button className="secundario" disabled>Convidar pessoa</button>
      </Cabecalho>
      <AvisoExemplo />
      <div className="grelha-equipa">
        <div className="painel">
          <h2 className="titulo-fita">Quem somos <span className="conta">{PESSOAS.length}</span></h2>
          <ul className="pessoas">
            {PESSOAS.map(([nome, papel]) => (
              <li key={nome}><span className="avatar">{iniciais(nome)}</span><div><strong>{nome}</strong><span>{papel}</span></div></li>
            ))}
          </ul>
        </div>
        <div className="coluna">
          <div className="painel">
            <h2 className="titulo-fita">O nosso trabalho <span className="conta">{TRABALHO.length}</span></h2>
            <ul className="linhas">
              {TRABALHO.map(([titulo, estado, nome, quem]) => (
                <li key={titulo}><span>{titulo}</span><span className={`estado estado-${estado}`}>{nome}</span><span className="avatar" title={quem}>{iniciais(quem)}</span></li>
              ))}
            </ul>
          </div>
          <div className="painel">
            <h2 className="titulo-fita">Pedidos que seguimos <span className="conta">{SEGUIMOS.length}</span></h2>
            <ul className="linhas">
              {SEGUIMOS.map(([titulo, estado, nome, votos]) => (
                <li key={titulo}><span>{titulo}</span><span className={`estado estado-${estado}`}>{nome}</span><span className="votos">{votos}</span></li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
