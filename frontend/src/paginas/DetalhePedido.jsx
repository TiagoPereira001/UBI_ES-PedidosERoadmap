import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ESTADOS } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Conversa from "../componentes/Conversa.jsx";
import { diaMes } from "../componentes/formatos.js";

// Ecrã 04. Estado, etiquetas, votos (só o total), conversa e histórico.
// Os botões de mudar estado vêm do servidor (pode_mudar_para): o ecrã não repete as regras.
export default function DetalhePedido({ utilizador }) {
  const { id } = useParams();
  const [pedido, setPedido] = useState(null);
  const [motivo, setMotivo] = useState("");
  const [etiquetas, setEtiquetas] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .pedido(id)
      .then((p) => {
        setPedido(p);
        setEtiquetas(p.etiquetas.join(", "));
      })
      .catch(() => setErro("Pedido não encontrado."));
  }, [id, utilizador]);

  async function votar() {
    const r = await api.votar(id);
    setPedido({ ...pedido, total_votos: r.total_votos, votei: r.votei });
  }

  async function mudar(para) {
    setErro("");
    try {
      setPedido(await api.mudarEstado(id, para, motivo));
      setMotivo("");
    } catch (falha) {
      setErro(falha.dados?.erro || falha.dados?.detail || "Não foi possível mudar o estado.");
    }
  }

  async function guardarEtiquetas(evento) {
    evento.preventDefault();
    setErro("");
    try {
      const atualizado = await api.classificar(id, { etiquetas: etiquetas.split(",") });
      setPedido(atualizado);
      setEtiquetas(atualizado.etiquetas.join(", "));
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível guardar as etiquetas.");
    }
  }

  if (erro && !pedido) return <p role="alert">{erro}</p>;
  if (!pedido) return <p>A carregar...</p>;

  const gere = utilizador && ["product_manager", "product_owner"].includes(utilizador.papel);
  const seguintes = pedido.pode_mudar_para || [];

  return (
    <section>
      <Cabecalho titulo={pedido.titulo} sub={`#${pedido.id} · ${pedido.categoria_nome} · submetido por ${pedido.autor} a ${diaMes(pedido.criado_em)}`}>
        <span className={`estado estado-${pedido.estado}`}>{pedido.estado_nome}</span>
        <span className="votos" aria-label={`${pedido.total_votos} votos`}>{pedido.total_votos}</span>
        {utilizador && <button className="secundario" onClick={votar}>{pedido.votei ? "Retirar voto" : "Votar"}</button>}
      </Cabecalho>

      <div className="grelha-lado">
        <div className="coluna">
          <div className="folha">
            {pedido.etiquetas.length > 0 && (
              <p className="etiquetas">{pedido.etiquetas.map((e) => <span key={e} className="etiqueta">{e}</span>)}</p>
            )}
            <p className="descricao">{pedido.descricao}</p>
          </div>
          <Conversa pedido={pedido.id} utilizador={utilizador} />
        </div>

        <aside className="coluna">
          <div className="painel">
            <h2 className="titulo-painel">Histórico</h2>
            <ol className="historico">
              {pedido.historico.map((h, i) => (
                <li key={i}>
                  <span className={`estado estado-${h.para}`}>{ESTADOS[h.para]}</span>
                  <span className="suave">{h.autor} · {new Date(h.quando).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" })}</span>
                  {h.motivo && <span className="motivo">Motivo: {h.motivo}</span>}
                </li>
              ))}
            </ol>
          </div>
          {seguintes.length > 0 && (
            <div className="painel">
              <h2 className="titulo-painel">Mudar estado</h2>
              {seguintes.includes("rejeitado") && (
                <>
                  <label htmlFor="motivo">Motivo (obrigatório para rejeitar)</label>
                  <textarea id="motivo" rows={2} value={motivo} onChange={(e) => setMotivo(e.target.value)} />
                </>
              )}
              <div className="botoes">
                {seguintes.map((para) => (
                  <button key={para} className={para === "rejeitado" ? "secundario" : undefined} onClick={() => mudar(para)}>{ESTADOS[para]}</button>
                ))}
              </div>
            </div>
          )}
          {gere && (
            <form className="painel" onSubmit={guardarEtiquetas}>
              <h2 className="titulo-painel">Etiquetas</h2>
              <label htmlFor="etiquetas">Etiquetas (separadas por vírgulas)</label>
              <input id="etiquetas" value={etiquetas} onChange={(e) => setEtiquetas(e.target.value)} />
              <button type="submit" className="secundario">Guardar etiquetas</button>
            </form>
          )}
          {erro && <p role="alert">{erro}</p>}
        </aside>
      </div>
    </section>
  );
}
