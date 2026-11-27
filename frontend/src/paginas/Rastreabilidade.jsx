import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";

const contem = (linha, texto) =>
  [linha.titulo, ...linha.historias.flatMap((h) => [h.texto, ...h.ligacoes.flatMap((l) => [l.url, l.descricao])])]
    .some((t) => t.toLowerCase().includes(texto.toLowerCase()));

function LigarCodigo({ historia, aoLigar }) {
  const [url, setUrl] = useState("");
  const [descricao, setDescricao] = useState("");
  async function enviar(e) {
    e.preventDefault();
    if (await aoLigar(historia.id, { url, descricao })) {
      setUrl("");
      setDescricao("");
    }
  }
  return (
    <form onSubmit={enviar}>
      <label>Endereço do commit<input type="url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/..." required /></label>
      <label>O que foi feito<input value={descricao} onChange={(e) => setDescricao(e.target.value)} maxLength={120} required /></label>
      <button className="secundario pequeno">Ligar</button>
    </form>
  );
}

// Ecrã 11. Do pedido chega-se ao código, e procurando o commit volta-se ao pedido (Helena, US-19).
export default function Rastreabilidade({ utilizador }) {
  const [linhas, setLinhas] = useState(null);
  const [procura, setProcura] = useState("");
  const [soFalta, setSoFalta] = useState(false);
  const [erro, setErro] = useState("");
  const marca = utilizador?.papel === "product_owner";
  const liga = marca || utilizador?.papel === "programador";

  const carregar = () => api.rastreabilidade().then(setLinhas);

  useEffect(() => {
    carregar().catch(() => setErro("Não foi possível carregar a rastreabilidade."));
  }, []);

  async function fazer(acao) {
    setErro("");
    try {
      await acao();
      await carregar();
      return true;
    } catch (falha) {
      setErro(falha.dados?.erro || falha.dados?.url?.[0] || "Não foi possível guardar.");
      return false;
    }
  }

  if (!linhas) return erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>;
  const porLigar = linhas.filter((l) => l.falta.length).length;
  const visiveis = linhas.filter((l) => contem(l, procura) && (!soFalta || l.falta.length));

  return (
    <section>
      <Cabecalho titulo="Rastreabilidade" sub={`${linhas.length} pedidos aprovados · ${porLigar} com alguma coisa por ligar`} />
      {erro && <p role="alert">{erro}</p>}
      <label>Procurar por pedido, user story ou commit<input type="search" value={procura} onChange={(e) => setProcura(e.target.value)} /></label>
      <label className="opcao"><input type="checkbox" checked={soFalta} onChange={(e) => setSoFalta(e.target.checked)} /> Só o que falta ligar</label>
      {!visiveis.length && <p className="nota">Nenhum pedido corresponde à procura.</p>}
      {visiveis.map((l) => (
        <article key={l.id} aria-label={l.titulo}>
          <div className="cadeia">
            <div className="cartao elo">
              <h2 className="titulo-mao"><Icone nome="pedidos" /> Pedido</h2>
              <Link to={`/pedidos/${l.id}`}><strong>{l.titulo}</strong></Link>
              <span className="suave">#{l.id} · {l.autor}</span>
              <div className="meta-pedido"><span className={`estado estado-${l.estado}`}>{l.estado_nome}</span></div>
              {l.falta.map((f) => <span key={f} className="alerta">{f}</span>)}
            </div>
            <span className="seta-entre" aria-hidden="true"><Icone nome="seta" /></span>
            <div className="cartao elo">
              <h2 className="titulo-mao"><Icone nome="requisitos" /> User stories</h2>
              {l.historias.map((h) => (
                <div key={h.id}>
                  <strong>{h.texto}</strong>
                  <p className="suave">{h.criterios.filter((c) => c.cumprido).length} de {h.criterios.length} critérios cumpridos</p>
                  {h.criterios.map((c) => (
                    <label key={c.id} className="opcao">
                      <input type="checkbox" checked={c.cumprido} disabled={!marca} onChange={(e) => fazer(() => api.marcarCriterio(c.id, e.target.checked))} /> {c.texto}
                    </label>
                  ))}
                </div>
              ))}
              {!l.historias.length && <Link to="/requisitos/gerar">Gerar user stories</Link>}
            </div>
            <span className="seta-entre" aria-hidden="true"><Icone nome="seta" /></span>
            <div className="cartao elo">
              <h2 className="titulo-mao"><Icone nome="codigo" /> Implementação</h2>
              <span className="suave">{[l.sprint || "sem sprint", l.equipa, ...l.releases].filter(Boolean).join(" · ")}</span>
              {l.historias.map((h) => (
                <div key={h.id}>
                  {l.historias.length > 1 && <span className="suave">{h.texto}</span>}
                  {h.ligacoes.map((c) => (
                    <p key={c.id}><a href={c.url} target="_blank" rel="noreferrer">{c.descricao}</a> <span className="suave">{c.criada_por}</span></p>
                  ))}
                  {liga && <LigarCodigo historia={h} aoLigar={(id, dados) => fazer(() => api.ligarCodigo(id, dados))} />}
                </div>
              ))}
            </div>
          </div>
        </article>
      ))}
    </section>
  );
}
