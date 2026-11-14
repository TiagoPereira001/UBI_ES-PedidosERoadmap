import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";
import { quando } from "../componentes/formatos.js";

const ICONE_DO_TIPO = { estado: "bandeira", mencao: "arroba", comentario: "conversa" };

const OPCOES = [
  ["mencoes", "alguém me menciona"],
  ["estados", "muda o estado de um pedido que sigo"],
  ["comentarios", "há comentários novos em pedidos que sigo"],
  ["email", "também por email"],
];

// Ecrã 12. Avisos curtos: o pedido e o que mudou (Sofia, US-22). Cada um escolhe o que recebe.
export default function Notificacoes({ utilizador }) {
  const [dados, setDados] = useState(null);
  const [prefs, setPrefs] = useState(null);
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!utilizador) return;
    Promise.all([api.notificacoes(), api.preferencias()])
      .then(([lista, escolhas]) => {
        setDados(lista);
        setPrefs(escolhas);
      })
      .catch(() => setErro("Não foi possível carregar as notificações."));
  }, [utilizador]);

  async function marcar(ids = []) {
    try {
      setDados(await api.marcarLidas(ids));
    } catch {
      setErro("Não foi possível marcar como lidas.");
    }
  }

  async function guardar(evento) {
    evento.preventDefault();
    try {
      setPrefs(await api.guardarPreferencias(prefs));
      setMensagem("Preferências guardadas.");
    } catch {
      setErro("Não foi possível guardar as preferências.");
    }
  }

  if (!utilizador) {
    return (
      <section>
        <Cabecalho titulo="Notificações" />
        <p><Link to="/entrar">Entra</Link> para veres as tuas notificações.</p>
      </section>
    );
  }
  if (!dados || !prefs) return erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>;

  return (
    <section>
      <Cabecalho titulo="Notificações" sub={`${dados.por_ler} por ler`}>
        {dados.por_ler > 0 && <button className="secundario" onClick={() => marcar()}>Marcar todas como lidas</button>}
      </Cabecalho>
      <div className="grelha-lado">
        <div className="coluna">
          {dados.itens.length === 0 ? (
            <div className="painel vazio"><p>Ainda não tens notificações.</p></div>
          ) : (
            <ul className="painel notificacoes">
              {dados.itens.map((n) => (
                <li key={n.id} className={n.lida ? "lida" : "por-ler"}>
                  <span className="ponto" aria-label={n.lida ? undefined : "por ler"} />
                  <span className="avatar"><Icone nome={ICONE_DO_TIPO[n.tipo] || "sino"} tamanho={16} /></span>
                  {n.pedido ? (
                    <Link to={`/pedidos/${n.pedido}`} onClick={() => !n.lida && marcar([n.id])}>{n.texto}</Link>
                  ) : (
                    <span>{n.texto}</span>
                  )}
                  <span className="suave quando">{quando(n.criada_em)}</span>
                </li>
              ))}
            </ul>
          )}
          {erro && <p role="alert">{erro}</p>}
        </div>
        <aside className="coluna">
          <form className="painel" onSubmit={guardar}>
            <h2 className="titulo-mao">Avisa-me quando...</h2>
            {OPCOES.map(([campo, texto]) => (
              <label key={campo} className="opcao">
                <input type="checkbox" checked={prefs[campo]} onChange={(e) => setPrefs({ ...prefs, [campo]: e.target.checked })} />
                {texto}
              </label>
            ))}
            <button type="submit">Guardar preferências</button>
            {mensagem && <p className="nota">{mensagem}</p>}
          </form>
        </aside>
      </div>
    </section>
  );
}
