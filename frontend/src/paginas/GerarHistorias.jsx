import { useEffect, useState } from "react";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";

const SERVICOS = { gemini: "Gemini (Google)", claude: "Claude (Anthropic)" };

// Ecrã 10. As user stories geradas são propostas: só ficam guardadas as que o Product Owner aceitar,
// com as edições que fizer (Ricardo). Sem chave de IA, as propostas vêm de um modelo local.
export default function GerarHistorias({ utilizador }) {
  const [pedidos, setPedidos] = useState(null);
  const [escolhido, setEscolhido] = useState("");
  const [dados, setDados] = useState(null);
  const [gerado, setGerado] = useState(null);
  const [aEditar, setAEditar] = useState(null);
  const [vista, setVista] = useState(null);
  const [erro, setErro] = useState("");
  const eProductOwner = utilizador?.papel === "product_owner";

  useEffect(() => {
    api.pedidosRequisitos()
      .then((lista) => { setPedidos(lista); if (lista.length) setEscolhido(String(lista[0].id)); })
      .catch(() => setErro("Não foi possível carregar os pedidos."));
  }, []);

  useEffect(() => {
    if (!escolhido) return;
    setGerado(null);
    setVista(null);
    api.historias(escolhido).then(setDados).catch(() => setErro("Não foi possível carregar as user stories."));
  }, [escolhido]);

  async function gerar() {
    setErro("");
    try {
      const r = await api.propostas(escolhido);
      setGerado({ ...r, propostas: r.propostas.map((p, i) => ({ ...p, chave: i })) });
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível gerar propostas.");
    }
  }

  async function aceitar(proposta) {
    setErro("");
    try {
      const origem = gerado.fonte === "ia" ? "ia" : "local";
      const historia = await api.aceitarHistoria(escolhido, { texto: proposta.texto, criterios: proposta.criterios, origem });
      setGerado({ ...gerado, propostas: gerado.propostas.filter((p) => p.chave !== proposta.chave) });
      setAEditar(null);
      setVista(historia);
      setDados(await api.historias(escolhido));
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível aceitar a user story.");
    }
  }

  const rejeitar = (chave) => setGerado({ ...gerado, propostas: gerado.propostas.filter((p) => p.chave !== chave) });
  const editar = (chave, texto) => setGerado({ ...gerado, propostas: gerado.propostas.map((p) => (p.chave === chave ? { ...p, texto } : p)) });

  if (!pedidos) return erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>;
  if (!pedidos.length) {
    return (
      <section>
        <Cabecalho titulo="User stories do pedido" sub="Ainda não há pedidos aprovados." />
        <p className="nota">As user stories geram-se a partir de um pedido aprovado.</p>
      </section>
    );
  }

  const pedido = dados?.pedido;
  const aceites = dados?.historias || [];
  const criterios = (vista || aceites[aceites.length - 1])?.criterios || [];

  return (
    <section>
      <Cabecalho titulo="User stories do pedido" sub={pedido ? `«${pedido.titulo}» · ${aceites.length} aceite${aceites.length === 1 ? "" : "s"}` : ""}>
        <select className="filtro" aria-label="Pedido" value={escolhido} onChange={(e) => setEscolhido(e.target.value)}>
          {pedidos.map((p) => <option key={p.id} value={p.id}>{p.titulo}</option>)}
        </select>
        {eProductOwner && <button onClick={gerar}>{gerado ? "Gerar de novo" : "Gerar propostas"}</button>}
      </Cabecalho>
      {erro && <p role="alert">{erro}</p>}
      {gerado && (
        <p className="nota">
          {gerado.fonte === "ia"
            ? `Propostas feitas pelo ${SERVICOS[gerado.servico] ?? "serviço de IA"}. Revê antes de aceitar.`
            : "O serviço de IA não está disponível. Estas propostas foram montadas pelo modelo local, a partir do título e da descrição."}
        </p>
      )}
      <div className="tres-colunas">
        {pedido && (
          <div className="cartao origem">
            <span className="rotulo">Pedido de origem</span>
            <strong>{pedido.titulo}</strong>
            <p>{pedido.descricao}</p>
            <div className="meta-pedido"><span className={`estado estado-${pedido.estado}`}>{pedido.estado_nome}</span></div>
          </div>
        )}
        <ul className="historias">
          {aceites.map((h) => (
            <li key={`h${h.id}`} className="cartao">
              <p>{h.texto}</p>
              <div className="meta-pedido">
                <span className="estado estado-concluido">Aceite</span>
                <span className="suave">{h.origem_nome} · aceite por {h.aceite_por}</span>
                <button className="secundario pequeno" onClick={() => setVista(h)}>Ver critérios</button>
              </div>
            </li>
          ))}
          {gerado?.propostas.map((p) => (
            <li key={`p${p.chave}`} className="cartao">
              {aEditar === p.chave ? (
                <textarea aria-label="Texto da user story" value={p.texto} onChange={(e) => editar(p.chave, e.target.value)} />
              ) : (
                <p>{p.texto}</p>
              )}
              <div className="botoes">
                <button className="pequeno" onClick={() => aceitar(p)}>Aceitar</button>
                <button className="secundario pequeno" onClick={() => setAEditar(aEditar === p.chave ? null : p.chave)}>{aEditar === p.chave ? "Feito" : "Editar"}</button>
                <button className="secundario pequeno" onClick={() => rejeitar(p.chave)}>Rejeitar</button>
              </div>
            </li>
          ))}
          {!aceites.length && !gerado && <li className="nota">Este pedido ainda não tem user stories.{eProductOwner && " Carrega em «Gerar propostas»."}</li>}
        </ul>
        <div className="painel">
          <h2 className="titulo-mao">Critérios de aceitação</h2>
          {criterios.length ? (
            <ul className="linhas">{criterios.map((c) => <li key={c.id}>{c.texto}</li>)}</ul>
          ) : (
            <p className="nota">Aparecem aqui os critérios da user story aceite.</p>
          )}
        </div>
      </div>
    </section>
  );
}
