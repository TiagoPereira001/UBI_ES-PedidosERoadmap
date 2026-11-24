import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ESTADOS } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Conversa from "../componentes/Conversa.jsx";
import { diaMes } from "../componentes/formatos.js";

function dataHora(iso) {
  return new Date(iso).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });
}

// Ecrã 04. Estado, etiquetas, votos (só o total), conversa, histórico e versões (US-03).
// Os botões de mudar estado e de editar vêm do servidor: o ecrã não repete as regras.
export default function DetalhePedido({ utilizador }) {
  const { id } = useParams();
  const [pedido, setPedido] = useState(null);
  const [motivo, setMotivo] = useState("");
  const [etiquetas, setEtiquetas] = useState("");
  const [erro, setErro] = useState("");
  const [aEditar, setAEditar] = useState(false);
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [versoes, setVersoes] = useState([]);
  const [escolhidas, setEscolhidas] = useState([]);

  async function carregarVersoes() {
    try {
      setVersoes(await api.versoes(id));
    } catch {
      setVersoes([]);
    }
  }

  useEffect(() => {
    api
      .pedido(id)
      .then((p) => {
        setPedido(p);
        setEtiquetas(p.etiquetas.join(", "));
        setTitulo(p.titulo);
        setDescricao(p.descricao);
      })
      .catch(() => setErro("Pedido não encontrado."));
    carregarVersoes();
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

  async function guardarEdicao(evento) {
    evento.preventDefault();
    setErro("");
    try {
      const atualizado = await api.editarPedido(id, { titulo, descricao });
      setPedido(atualizado);
      setTitulo(atualizado.titulo);
      setDescricao(atualizado.descricao);
      setAEditar(false);
      setEscolhidas([]);
      await carregarVersoes();
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível guardar a edição.");
    }
  }

  async function repor(versaoId) {
    setErro("");
    try {
      const atualizado = await api.reporVersao(id, versaoId);
      setPedido(atualizado);
      setTitulo(atualizado.titulo);
      setDescricao(atualizado.descricao);
      setAEditar(false);
      setEscolhidas([]);
      await carregarVersoes();
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível repor a versão.");
    }
  }

  function alternarEscolha(versaoId) {
    setEscolhidas((atuais) => {
      if (atuais.includes(versaoId)) return atuais.filter((x) => x !== versaoId);
      if (atuais.length >= 2) return [atuais[1], versaoId];
      return [...atuais, versaoId];
    });
  }

  if (erro && !pedido) return <p role="alert">{erro}</p>;
  if (!pedido) return <p>A carregar...</p>;

  const gere = utilizador && ["product_manager", "product_owner"].includes(utilizador.papel);
  const seguintes = pedido.pode_mudar_para || [];
  const comparar = escolhidas.map((vid) => versoes.find((v) => v.id === vid)).filter(Boolean);

  return (
    <section>
      <Cabecalho titulo={pedido.titulo} sub={`#${pedido.id} · ${pedido.categoria_nome} · submetido por ${pedido.autor} a ${diaMes(pedido.criado_em)}`}>
        <span className={`estado estado-${pedido.estado}`}>{pedido.estado_nome}</span>
        <span className="votos" aria-label={`${pedido.total_votos} votos`}>{pedido.total_votos}</span>
        {utilizador && <button className="secundario" onClick={votar}>{pedido.votei ? "Retirar voto" : "Votar"}</button>}
        {pedido.pode_editar && !aEditar && (
          <button type="button" onClick={() => { setAEditar(true); setTitulo(pedido.titulo); setDescricao(pedido.descricao); setErro(""); }}>
            Editar
          </button>
        )}
      </Cabecalho>

      <div className="grelha-lado">
        <div className="coluna">
          <div className="folha">
            {pedido.etiquetas.length > 0 && (
              <p className="etiquetas">{pedido.etiquetas.map((e) => <span key={e} className="etiqueta">{e}</span>)}</p>
            )}
            {aEditar ? (
              <form onSubmit={guardarEdicao}>
                <label htmlFor="titulo-pedido">Título</label>
                <input id="titulo-pedido" value={titulo} onChange={(e) => setTitulo(e.target.value)} maxLength={120} required />
                <label htmlFor="descricao-pedido">Descrição</label>
                <textarea id="descricao-pedido" rows={6} value={descricao} onChange={(e) => setDescricao(e.target.value)} required />
                <div className="botoes">
                  <button type="submit">Guardar</button>
                  <button type="button" className="secundario" onClick={() => { setAEditar(false); setErro(""); }}>Cancelar</button>
                </div>
              </form>
            ) : (
              <p className="descricao">{pedido.descricao}</p>
            )}
          </div>
          {versoes.length > 0 && (
            <div className="painel">
              <h2 className="titulo-painel">Versões</h2>
              <p className="suave">Escolhe duas para comparar lado a lado.</p>
              <ol className="historico">
                {versoes.map((v, i) => (
                  <li key={v.id}>
                    <label>
                      <input
                        type="checkbox"
                        checked={escolhidas.includes(v.id)}
                        onChange={() => alternarEscolha(v.id)}
                        aria-label={`Escolher versão ${i + 1}`}
                      />
                      {" "}Versão {i + 1} · {v.autor} · {dataHora(v.quando)}
                    </label>
                    <span className="suave">{v.titulo}</span>
                    {pedido.pode_editar && (
                      <button type="button" className="secundario" onClick={() => repor(v.id)}>Repor</button>
                    )}
                  </li>
                ))}
              </ol>
              {comparar.length === 2 && (
                <div className="campos-lado">
                  {comparar.map((v) => (
                    <div key={v.id} className="folha">
                      <h3 className="titulo-painel">Versão {versoes.findIndex((x) => x.id === v.id) + 1}</h3>
                      <p className="suave">{v.autor} · {dataHora(v.quando)}</p>
                      <p><strong>{v.titulo}</strong></p>
                      <p className="descricao">{v.descricao}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          <Conversa pedido={pedido.id} utilizador={utilizador} />
        </div>

        <aside className="coluna">
          <div className="painel">
            <h2 className="titulo-painel">Histórico</h2>
            <ol className="historico">
              {pedido.historico.map((h, i) => (
                <li key={i}>
                  <span className={`estado estado-${h.para}`}>{ESTADOS[h.para]}</span>
                  <span className="suave">{h.autor} · {dataHora(h.quando)}</span>
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
