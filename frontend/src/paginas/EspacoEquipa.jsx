import { useEffect, useState } from "react";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import { iniciais, nomeDoPapel, quando } from "../componentes/formatos.js";

// Ecrã 13. Cada equipa tem o seu espaço: quem lá está, o trabalho que tem por acabar e a conversa (US-24).
// Escrevem na conversa os membros e o gestor de projeto; só o gestor (a Helena) muda quem faz parte.
export default function EspacoEquipa({ utilizador }) {
  const [equipas, setEquipas] = useState(null);
  const [escolhida, setEscolhida] = useState("");
  const [espaco, setEspaco] = useState(null);
  const [texto, setTexto] = useState("");
  const [pessoas, setPessoas] = useState([]);
  const [nova, setNova] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.equipas()
      .then((lista) => { setEquipas(lista); if (lista.length) setEscolhida(String(lista[0].id)); })
      .catch(() => setErro("Não foi possível carregar as equipas."));
  }, []);

  useEffect(() => {
    if (escolhida) api.espacoEquipa(escolhida).then(setEspaco).catch(() => setErro("Não foi possível carregar a equipa."));
  }, [escolhida, utilizador]);

  useEffect(() => {
    if (espaco?.pode_gerir && !pessoas.length) api.pessoas().then(setPessoas).catch(() => {});
  }, [espaco]);

  async function enviar(evento) {
    evento.preventDefault();
    setErro("");
    try {
      setEspaco(await api.escreverNaEquipa(escolhida, texto));
      setTexto("");
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível enviar a mensagem.");
    }
  }

  async function juntar() {
    setErro("");
    try {
      setEspaco(await api.juntarAEquipa(escolhida, nova));
      setNova("");
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível juntar a pessoa à equipa.");
    }
  }

  if (!equipas) return erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>;
  if (!equipas.length) return <section><Cabecalho titulo="Equipa" sub="Ainda não há equipas." /></section>;
  if (!espaco) return <p>A carregar...</p>;

  const fora = pessoas.filter((p) => !espaco.membros.some((m) => m.username === p));

  return (
    <section>
      <Cabecalho titulo={espaco.equipa.nome} sub={`${espaco.membros.length} pessoa${espaco.membros.length === 1 ? "" : "s"} · ${espaco.trabalho.length} por acabar`}>
        <select className="filtro" aria-label="Equipa" value={escolhida} onChange={(e) => setEscolhida(e.target.value)}>
          {equipas.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
        </select>
      </Cabecalho>
      {erro && <p role="alert">{erro}</p>}
      <div className="grelha-equipa">
        <div className="painel">
          <h2 className="titulo-fita">Quem somos <span className="conta">{espaco.membros.length}</span></h2>
          <ul className="pessoas">
            {espaco.membros.map((m) => (
              <li key={m.id}><span className="avatar">{iniciais(m.username)}</span><div><strong>{m.username}</strong><span>{nomeDoPapel(m.papel)}</span></div></li>
            ))}
          </ul>
          {!espaco.membros.length && <p className="nota">Ainda ninguém faz parte desta equipa.</p>}
          {espaco.pode_gerir && (
            <div className="botoes">
              <select aria-label="Pessoa a juntar" value={nova} onChange={(e) => setNova(e.target.value)}>
                <option value="">Escolher pessoa</option>
                {fora.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
              <button className="secundario pequeno" onClick={juntar} disabled={!nova}>Juntar à equipa</button>
            </div>
          )}
        </div>
        <div className="coluna">
          <div className="painel">
            <h2 className="titulo-fita">O nosso trabalho <span className="conta">{espaco.trabalho.length}</span></h2>
            <ul className="linhas">
              {espaco.trabalho.map((t) => (
                <li key={t.pedido}><span>{t.titulo}</span><span className={`estado estado-${t.estado}`}>{t.estado_nome}</span><span className="suave">{t.sprint || "no backlog"}</span></li>
              ))}
            </ul>
            {!espaco.trabalho.length && <p className="nota">A equipa não tem trabalho atribuído por acabar.</p>}
          </div>
          <div className="painel">
            <h2 className="titulo-fita">Conversa da equipa <span className="conta">{espaco.mensagens.length}</span></h2>
            <ul className="linhas">
              {espaco.mensagens.map((m) => (
                <li key={m.id}><span><strong>{m.autor}</strong> {m.texto}</span><span className="suave">{quando(m.criada_em)}</span></li>
              ))}
            </ul>
            {espaco.pode_escrever ? (
              <form onSubmit={enviar}>
                <label htmlFor="mensagem">Mensagem</label>
                <textarea id="mensagem" value={texto} onChange={(e) => setTexto(e.target.value)} required />
                <button type="submit">Enviar</button>
              </form>
            ) : (
              <p className="nota">Só os membros da equipa e o gestor de projeto escrevem aqui.</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
