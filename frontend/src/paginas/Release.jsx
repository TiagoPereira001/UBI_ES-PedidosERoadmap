import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ESTADOS } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";

const ESTADOS_MILESTONE = { por_comecar: "Por começar", em_curso: "Em curso", concluido: "Concluído" };

function metaPedido(pedido, dependencias) {
  const deps = dependencias.filter((d) => d.pedido === pedido.id);
  if (deps.length === 0) return "sem dependências";
  return "depende de: " + deps.map((d) => d.depende_de_titulo).join(", ");
}

// Ecrã 09. Funcionalidades da release, dependências e milestones (US-16, US-17).
export default function Release({ utilizador }) {
  const { id } = useParams();
  const [release, setRelease] = useState(null);
  const [erro, setErro] = useState("");
  const [pedidoNovo, setPedidoNovo] = useState("");
  const [depDe, setDepDe] = useState("");
  const [depPara, setDepPara] = useState("");
  const [milestone, setMilestone] = useState({ nome: "", data: "" });
  const [pedidoMilestone, setPedidoMilestone] = useState({});
  const podePlanear = utilizador?.papel === "product_manager";
  const podeDependencia = utilizador && ["product_manager", "programador"].includes(utilizador.papel);

  async function fazer(acao) {
    setErro("");
    try {
      await acao();
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível concluir a ação.");
    }
  }

  const carregar = () =>
    api
      .release(id)
      .then(setRelease)
      .catch(() => setErro("Não foi possível carregar a release."));

  useEffect(() => {
    carregar();
  }, [id]);

  if (!release) {
    return (
      <section>
        <Cabecalho titulo="Release" />
        {erro ? <p role="alert">{erro}</p> : <p>A carregar...</p>}
      </section>
    );
  }

  const dataPrevista = new Date(release.data_prevista).toLocaleDateString("pt-PT");
  const dependencias = release.dependencias || [];
  const avisos = release.avisos || [];
  const milestones = release.milestones || [];
  const aprovados = release.aprovados || [];
  const idsNaRelease = new Set(release.pedidos.map((p) => p.id));
  const paraAcrescentar = aprovados.filter((p) => !idsNaRelease.has(p.id));
  const dependeDeOpcoes = aprovados.filter((p) => String(p.id) !== depDe);

  return (
    <section>
      <Cabecalho
        titulo={release.nome}
        sub={`data prevista: ${dataPrevista} · ${release.pedidos.length} funcionalidade${release.pedidos.length === 1 ? "" : "s"} · ${release.progresso}% feito`}
      >
        <Link to="/roadmap" className="botao secundario">Voltar ao roadmap</Link>
        {podePlanear && !release.lancada_em && (
          <button type="button" onClick={() => fazer(async () => setRelease(await api.lancarRelease(id)))}>
            Lançar release
          </button>
        )}
      </Cabecalho>
      {erro && <p role="alert">{erro}</p>}
      <div className="grelha-lado">
        <div className="coluna">
          <div className="painel">
            <h2 className="titulo-fita">Funcionalidades <span className="conta">{release.pedidos.length}</span></h2>
            {release.pedidos.length === 0 ? (
              <p className="nota">Ainda não há pedidos nesta release.</p>
            ) : (
              <ul className="cartoes">
                {release.pedidos.map((p) => (
                  <li key={p.id} className="cartao">
                    <div className="linha-cartao">
                      <Link to={`/pedidos/${p.id}`} className="titulo-cartao">{p.titulo}</Link>
                      <span className={`estado estado-${p.estado}`}>{p.estado_nome || ESTADOS[p.estado]}</span>
                    </div>
                    <div className="meta-cartao">{metaPedido(p, dependencias)}</div>
                    {podePlanear && (
                      <button type="button" className="secundario pequeno" onClick={() => fazer(async () => setRelease(await api.tirarDaRelease(id, p.id)))}>
                        Tirar
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
            {podePlanear && (
              <form
                className="botoes"
                onSubmit={(evento) => {
                  evento.preventDefault();
                  fazer(async () => {
                    setRelease(await api.porNaRelease(id, Number(pedidoNovo)));
                    setPedidoNovo("");
                  });
                }}
              >
                <label htmlFor="pedido-release">Pedido</label>
                <select id="pedido-release" value={pedidoNovo} onChange={(e) => setPedidoNovo(e.target.value)} required>
                  <option value="">Escolhe um pedido</option>
                  {paraAcrescentar.map((p) => (
                    <option key={p.id} value={p.id}>{p.titulo}</option>
                  ))}
                </select>
                <button type="submit">Adicionar funcionalidade</button>
              </form>
            )}
            {avisos.map((a) => (
              <div key={`${a.pedido_id}-${a.depende_de_id}`} className="postit coral" role="status">
                <p>{a.mensagem}</p>
              </div>
            ))}
            {dependencias.length > 0 && (
              <div>
                <h3 className="titulo-painel">Dependências</h3>
                <ul className="linhas">
                  {dependencias.map((d) => (
                    <li key={d.id}>
                      <span>{d.pedido_titulo} → {d.depende_de_titulo}</span>
                      {podeDependencia && (
                        <button
                          type="button"
                          className="secundario"
                          onClick={() => fazer(async () => {
                            await api.apagarDependencia(d.id);
                            await carregar();
                          })}
                        >
                          Apagar
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {podeDependencia && (
              <form
                onSubmit={(evento) => {
                  evento.preventDefault();
                  fazer(async () => {
                    await api.criarDependencia({ pedido: Number(depDe), depende_de: Number(depPara) });
                    setDepDe("");
                    setDepPara("");
                    await carregar();
                  });
                }}
              >
                <h3 className="titulo-painel">Nova dependência</h3>
                <div className="campos-lado">
                  <div>
                    <label htmlFor="dep-de">Pedido</label>
                    <select id="dep-de" value={depDe} onChange={(e) => { setDepDe(e.target.value); setDepPara(""); }} required>
                      <option value="">Escolhe</option>
                      {release.pedidos.map((p) => (
                        <option key={p.id} value={p.id}>{p.titulo}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="dep-para">Depende de</label>
                    <select id="dep-para" value={depPara} onChange={(e) => setDepPara(e.target.value)} required>
                      <option value="">Escolhe</option>
                      {dependeDeOpcoes.map((p) => (
                        <option key={p.id} value={p.id}>{p.titulo}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <button type="submit" className="secundario">Adicionar dependência</button>
              </form>
            )}
          </div>
        </div>
        <aside className="painel">
          <h2 className="titulo-fita">Milestones <span className="conta">{milestones.length}</span></h2>
          {milestones.length === 0 && <p className="nota">Ainda não há milestones nesta release.</p>}
          <ul className="cartoes">
            {milestones.map((m) => {
              const idsNoMilestone = new Set(m.pedidos.map((p) => p.id));
              return (
                <li key={m.id} className="cartao">
                  <div className="linha-cartao">
                    <span className="titulo-cartao"><Icone nome="bandeira" tamanho={18} /> {m.nome}</span>
                    <span className="suave">{new Date(m.data).toLocaleDateString("pt-PT")} · {ESTADOS_MILESTONE[m.estado]}</span>
                  </div>
                  <ul className="linhas">
                    {m.pedidos.map((p) => (
                      <li key={p.id}>
                        <span>{p.titulo}</span>
                        {podePlanear && (
                          <button type="button" className="secundario pequeno" aria-label={`Tirar ${p.titulo} de ${m.nome}`}
                            onClick={() => fazer(async () => { await api.tirarDoMilestone(m.id, p.id); await carregar(); })}>
                            Tirar
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                  {podePlanear && (
                    <form
                      onSubmit={(evento) => {
                        evento.preventDefault();
                        fazer(async () => {
                          await api.porNoMilestone(m.id, Number(pedidoMilestone[m.id]));
                          setPedidoMilestone({ ...pedidoMilestone, [m.id]: "" });
                          await carregar();
                        });
                      }}
                    >
                      <label htmlFor={`pedido-milestone-${m.id}`}>Funcionalidade</label>
                      <select id={`pedido-milestone-${m.id}`} value={pedidoMilestone[m.id] || ""}
                        onChange={(e) => setPedidoMilestone({ ...pedidoMilestone, [m.id]: e.target.value })} required>
                        <option value="">Escolhe</option>
                        {aprovados.filter((p) => !idsNoMilestone.has(p.id)).map((p) => <option key={p.id} value={p.id}>{p.titulo}</option>)}
                      </select>
                      <div className="botoes">
                        <button type="submit" className="secundario pequeno">Pôr no milestone</button>
                        <button type="button" className="secundario pequeno"
                          onClick={() => {
                            if (!window.confirm(`Apagar o milestone «${m.nome}»?`)) return;
                            fazer(async () => { await api.apagarMilestone(m.id); await carregar(); });
                          }}>
                          Apagar milestone
                        </button>
                      </div>
                    </form>
                  )}
                </li>
              );
            })}
          </ul>
          {podePlanear && (
            <form
              onSubmit={(evento) => {
                evento.preventDefault();
                fazer(async () => {
                  await api.criarMilestone({ ...milestone, release: Number(id) });
                  setMilestone({ nome: "", data: "" });
                  await carregar();
                });
              }}
            >
              <label htmlFor="milestone-nome">Nome</label>
              <input id="milestone-nome" value={milestone.nome} onChange={(e) => setMilestone({ ...milestone, nome: e.target.value })} maxLength={80} required />
              <label htmlFor="milestone-data">Data</label>
              <input id="milestone-data" type="date" value={milestone.data} onChange={(e) => setMilestone({ ...milestone, data: e.target.value })} required />
              <button type="submit" className="secundario">Novo milestone</button>
            </form>
          )}
        </aside>
      </div>
    </section>
  );
}
