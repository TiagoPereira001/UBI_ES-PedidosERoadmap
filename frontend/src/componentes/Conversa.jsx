import { useEffect, useState } from "react";
import { api } from "../api.js";
import Icone from "./Icone.jsx";
import { iniciais, quando } from "./formatos.js";

// A conversa de um pedido (ecrã 04, US-21 e US-23). @nome chama a pessoa e ela recebe uma notificação.
export default function Conversa({ pedido, utilizador }) {
  const [comentarios, setComentarios] = useState([]);
  const [texto, setTexto] = useState("");
  const [pessoas, setPessoas] = useState([]);
  const [aEditar, setAEditar] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.comentarios(pedido).then(setComentarios).catch(() => setErro("Não foi possível carregar a conversa."));
  }, [pedido]);

  useEffect(() => {
    if (utilizador) api.pessoas().then(setPessoas).catch(() => {});
  }, [utilizador]);

  // Sugere nomes quando a última palavra começa por @.
  const ultima = texto.split(/\s/).pop();
  const sugestoes = ultima.startsWith("@") ? pessoas.filter((p) => p.startsWith(ultima.slice(1))).slice(0, 5) : [];

  function mencionar(nome) {
    setTexto(texto.slice(0, texto.length - ultima.length) + `@${nome} `);
  }

  async function tentar(acao, falhou) {
    setErro("");
    try {
      await acao();
      setComentarios(await api.comentarios(pedido));
    } catch (falha) {
      setErro(falha.dados?.erro || falhou);
    }
  }

  async function enviar(evento) {
    evento.preventDefault();
    await tentar(async () => {
      await api.comentar(pedido, texto);
      setTexto("");
    }, "Não foi possível enviar o comentário.");
  }

  function guardarEdicao(evento, id) {
    evento.preventDefault();
    tentar(async () => {
      await api.editarComentario(id, aEditar.texto);
      setAEditar(null);
    }, "Não foi possível editar.");
  }

  return (
    <section className="conversa" aria-label="Conversa">
      <h2 className="titulo-mao">Conversa</h2>
      {comentarios.length === 0 && <p className="nota">Ainda não há comentários.</p>}
      <ul>
        {comentarios.map((c) => (
          <li key={c.id}>
            <span className="avatar">{iniciais(c.autor)}</span>
            <div className="mensagem">
              <div className="quem-quando">
                {c.autor} · {quando(c.criado_em)}{c.editado_em && " · editado"}
              </div>
              {aEditar?.id === c.id ? (
                <form onSubmit={(e) => guardarEdicao(e, c.id)}>
                  <label htmlFor={`editar-${c.id}`}>Editar comentário</label>
                  <textarea id={`editar-${c.id}`} rows={2} value={aEditar.texto} onChange={(e) => setAEditar({ ...aEditar, texto: e.target.value })} />
                  <div className="botoes">
                    <button type="submit" className="pequeno">Guardar</button>
                    <button type="button" className="secundario pequeno" onClick={() => setAEditar(null)}>Cancelar</button>
                  </div>
                </form>
              ) : (
                <p>{c.texto}</p>
              )}
              {c.meu && aEditar?.id !== c.id && (
                <div className="acoes-comentario">
                  <button className="ligacao" onClick={() => setAEditar({ id: c.id, texto: c.texto })}>Editar</button>
                  <button className="ligacao" onClick={() => tentar(() => api.apagarComentario(c.id), "Não foi possível apagar.")}>Apagar</button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
      {utilizador ? (
        <form className="escrever" onSubmit={enviar}>
          <label htmlFor="comentario" className="so-leitor">Escreve um comentário. Usa @ para chamar alguém.</label>
          <div className="campo-comentario">
            <Icone nome="conversa" tamanho={18} />
            <textarea id="comentario" rows={1} value={texto} onChange={(e) => setTexto(e.target.value)}
              placeholder="Escreve um comentário. Usa @ para chamar alguém." />
          </div>
          {sugestoes.length > 0 && (
            <div className="sugestoes" aria-label="Pessoas">
              {sugestoes.map((nome) => (
                <button key={nome} type="button" className="secundario pequeno" onClick={() => mencionar(nome)}>@{nome}</button>
              ))}
            </div>
          )}
          <button type="submit" className="pequeno" disabled={!texto.trim()}>Comentar</button>
        </form>
      ) : (
        <p className="nota">Entra para comentar.</p>
      )}
      {erro && <p role="alert">{erro}</p>}
    </section>
  );
}
