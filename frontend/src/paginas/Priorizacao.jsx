import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import { quando } from "../componentes/formatos.js";

const ORDENS = [
  ["manual", "Ordem do Product Owner"],
  ["relacao", "Impacto por ponto de esforço"],
  ["impacto", "Impacto"],
  ["esforco", "Esforço (menor primeiro)"],
  ["votos", "Votos"],
];

function mover(lista, de, para) {
  const nova = [...lista];
  const [item] = nova.splice(de, 1);
  nova.splice(para, 0, item);
  return nova;
}

// Ecrã 05. A ordem é do Product Owner; a IA só sugere, e diz sempre porquê (Ricardo, US-06, US-08, US-09).
const SERVICOS = { gemini: "Gemini (Google)", claude: "Claude (Anthropic)" };

export default function Priorizacao({ utilizador }) {
  const [ordem, setOrdem] = useState("manual");
  const [dados, setDados] = useState(null);
  const [itens, setItens] = useState([]);
  const [mudou, setMudou] = useState(false);
  const [razao, setRazao] = useState("");
  const [sugestao, setSugestao] = useState(null);
  const [historico, setHistorico] = useState(null);
  const [erro, setErro] = useState("");

  const papel = utilizador?.papel;
  const eProductOwner = papel === "product_owner";
  const estimaEsforco = eProductOwner || papel === "programador";

  function mostrar(resposta) {
    setDados(resposta);
    setItens(resposta.itens);
    setMudou(false);
  }

  useEffect(() => {
    api.priorizacao({ ordem }).then(mostrar).catch(() => setErro("Não foi possível carregar a priorização."));
  }, [ordem]);

  async function tentar(acao, mensagem) {
    setErro("");
    try {
      await acao();
    } catch (falha) {
      setErro(falha.dados?.erro || mensagem);
    }
  }

  const estimar = (id, campo, valor) =>
    tentar(async () => mostrar(await api.estimar(id, { [campo]: Number(valor) })), "Não foi possível guardar a estimativa.");

  const guardar = (aceitouIa = false) =>
    tentar(async () => {
      const ids = aceitouIa ? sugestao.ordem_sugerida : itens.map((i) => i.id);
      const texto = aceitouIa && !razao ? "Aceitei a sugestão da IA." : razao;
      mostrar(await api.ordenar({ ids, razao: texto, aceitou_sugestao_ia: aceitouIa }));
      setRazao("");
      setSugestao(null);
      if (historico) setHistorico(await api.historicoOrdem());
    }, "Não foi possível guardar a ordem.");

  const pedirSugestao = () => tentar(async () => setSugestao(await api.sugestao()), "Não foi possível pedir a sugestão.");

  const verHistorico = () =>
    tentar(async () => setHistorico(historico ? null : await api.historicoOrdem()), "Não foi possível ver o histórico.");

  if (!dados) return erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>;

  const nivelDe = Object.fromEntries((sugestao?.sugestoes || []).map((s) => [s.pedido_id, s.nivel]));
  const podeMover = eProductOwner && ordem === "manual";
  const subtitulo = eProductOwner
    ? "Usa as setas para mudar a ordem. Fica registado quem mudou e porquê."
    : "A ordem é do Product Owner. Aqui vês a ordem atual.";

  return (
    <section>
      <Cabecalho titulo="Priorização" sub={subtitulo}>
        <button className="secundario" onClick={verHistorico}>{historico ? "Esconder histórico" : "Ver histórico"}</button>
        {eProductOwner && <button onClick={() => guardar(false)} disabled={!mudou && !razao}>Guardar ordem</button>}
      </Cabecalho>

      <div className="grelha-lado">
        <div className="coluna">
          <div className="ver-por">
            <label htmlFor="ordem">Ver por</label>
            <select id="ordem" value={ordem} onChange={(e) => setOrdem(e.target.value)}>
              {ORDENS.map(([valor, nome]) => <option key={valor} value={valor}>{nome}</option>)}
            </select>
          </div>

          {itens.length === 0 ? (
            <div className="painel vazio"><p>Não há pedidos em análise nem aprovados para priorizar.</p></div>
          ) : (
            <div className="painel tabela-painel">
              <table className="tabela-ordem">
                <thead>
                  <tr>
                    <th aria-label="Lugar"></th><th>Pedido</th><th>Votos</th><th>Impacto</th><th>Esforço (pontos)</th>
                    {sugestao && <th>A IA sugere</th>}
                    {podeMover && <th aria-label="Mover"></th>}
                  </tr>
                </thead>
                <tbody>
                  {itens.map((p, i) => (
                    <tr key={p.id} className={p.fora_da_capacidade ? "fora" : undefined}>
                      <td className="lugar">{p.posicao ?? "–"}</td>
                      <td>
                        <Link className="titulo-pedido" to={`/pedidos/${p.id}`}>{p.titulo}</Link>
                        <div className="meta-pedido"><span className={`estado estado-${p.estado}`}>{p.estado_nome}</span></div>
                      </td>
                      <td className="votos">{p.total_votos}</td>
                      <td>
                        {eProductOwner ? (
                          <select className="pequeno" aria-label={`Impacto de ${p.titulo}`} value={p.impacto ?? ""} onChange={(e) => estimar(p.id, "impacto", e.target.value)}>
                            <option value="" disabled>por estimar</option>
                            {dados.escala.impacto.map((n) => <option key={n.valor} value={n.valor}>{n.nome}</option>)}
                          </select>
                        ) : (
                          dados.escala.impacto.find((n) => n.valor === p.impacto)?.nome ?? "por estimar"
                        )}
                      </td>
                      <td>
                        {estimaEsforco ? (
                          <select className="pequeno" aria-label={`Esforço de ${p.titulo}`} value={p.esforco ?? ""} onChange={(e) => estimar(p.id, "esforco", e.target.value)}>
                            <option value="" disabled>sem estimativa</option>
                            {dados.escala.esforco.map((n) => <option key={n} value={n}>{n}</option>)}
                          </select>
                        ) : (
                          p.esforco ?? "sem estimativa"
                        )}
                      </td>
                      {sugestao && <td><span className="autocolante">{nivelDe[p.id]}</span></td>}
                      {podeMover && (
                        <td className="mover">
                          <button className="secundario pequeno" aria-label={`Subir ${p.titulo}`} disabled={i === 0} onClick={() => { setItens(mover(itens, i, i - 1)); setMudou(true); }}>↑</button>
                          <button className="secundario pequeno" aria-label={`Descer ${p.titulo}`} disabled={i === itens.length - 1} onClick={() => { setItens(mover(itens, i, i + 1)); setMudou(true); }}>↓</button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {dados.aviso && <p className="aviso">{dados.aviso}</p>}
          {erro && <p role="alert">{erro}</p>}

          {historico && (
            <div className="painel">
              <h2 className="titulo-painel">Histórico da ordem</h2>
              {historico.length === 0 && <p className="nota">A ordem ainda não foi mudada.</p>}
              <ol className="historico">
                {historico.map((h) => (
                  <li key={h.id}>
                    <span className="suave">{quando(h.quando)} · {h.autor}{h.aceitou_sugestao_ia && " · aceitou a sugestão da IA"}</span>
                    {h.razao && <span>{h.razao}</span>}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>

        {eProductOwner && (
          <aside className="coluna">
            <div className="painel">
              <h2 className="titulo-mao">Porque esta ordem?</h2>
              <label htmlFor="razao">Razão (fica no histórico)</label>
              <textarea id="razao" rows={3} value={razao} onChange={(e) => setRazao(e.target.value)} />
              {!sugestao ? (
                <button className="secundario largo" onClick={pedirSugestao}>Pedir sugestão da IA</button>
              ) : (
                <>
                  <button className="largo" onClick={() => guardar(true)}>Aceitar as sugestões</button>
                  <button className="secundario largo" onClick={() => setSugestao(null)}>Manter a minha ordem</button>
                </>
              )}
            </div>
            {sugestao && (
              <div className="postit">
                <h2 className="titulo-mao">Sugestão da IA</h2>
                {sugestao.fonte === "ia" ? (
                  <p className="nota-postit">Sugestão feita pelo {SERVICOS[sugestao.servico] ?? "serviço de IA"}. Só muda a ordem se a aceitares.</p>
                ) : (
                  <p className="nota-postit">O serviço de IA não está disponível. Esta sugestão foi feita com a regra local (votos, impacto e esforço).</p>
                )}
                <ol>
                  {sugestao.sugestoes.map((s) => (
                    <li key={s.pedido_id}>{s.titulo} ({s.nivel}). Razão: {s.razao}</li>
                  ))}
                </ol>
                <p className="nota-postit">A IA só sugere. Nada muda sem o Product Owner aceitar.</p>
              </div>
            )}
          </aside>
        )}
      </div>
    </section>
  );
}
