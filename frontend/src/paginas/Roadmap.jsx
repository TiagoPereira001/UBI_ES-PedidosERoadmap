import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";

const NOMES_MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
const ESTADOS_RELEASE = { planeada: "Planeada", em_curso: "Em curso", lancada: "Lançada" };
const MESES_VISIVEIS = 4;
const DIA = 24 * 60 * 60 * 1000;

// Os quatro meses a partir do mês da primeira release (ou do mês atual, se ainda não houver nenhuma).
export function janela(releases, hoje = new Date()) {
  const primeira = releases.length ? new Date(Math.min(...releases.map((r) => new Date(r.inicio)))) : hoje;
  const inicio = new Date(primeira.getFullYear(), primeira.getMonth(), 1);
  const fim = new Date(inicio.getFullYear(), inicio.getMonth() + MESES_VISIVEIS, 1);
  const meses = Array.from({ length: MESES_VISIVEIS }, (_, i) => NOMES_MESES[(inicio.getMonth() + i) % 12]);
  return { inicio, dias: Math.round((fim - inicio) / DIA), meses };
}

const VAZIO = { nome: "", inicio: "", data_prevista: "", objetivo: "" };

// Ecrã 08. Cada release é uma fita ao longo dos meses. A que está em curso leva fita amarela e a que
// está perto da data com pedidos por fazer fica marcada "Em risco" (Helena). Só a Marta cria releases.
export default function Roadmap({ utilizador }) {
  const [releases, setReleases] = useState(null);
  const [nova, setNova] = useState(null);
  const [erro, setErro] = useState("");
  const podePlanear = utilizador?.papel === "product_manager";
  const mudar = (campo) => (e) => setNova({ ...nova, [campo]: e.target.value });

  const carregar = () => api.roadmap().then((r) => setReleases(r.releases)).catch(() => setErro("Não foi possível carregar o roadmap."));
  useEffect(() => { carregar(); }, []);

  async function criar(evento) {
    evento.preventDefault();
    setErro("");
    try {
      await api.criarRelease(nova);
      setNova(null);
      await carregar();
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível criar a release. Confirma o nome e as datas.");
    }
  }

  if (!releases) return <section><Cabecalho titulo="Roadmap" />{erro && <p role="alert">{erro}</p>}</section>;

  const { inicio, dias, meses } = janela(releases);
  const dia = (data) => Math.min(Math.max((new Date(data) - inicio) / DIA, 0), dias);
  const pos = (d) => `${(d / dias) * 100}%`;
  const hoje = (Date.now() - inicio) / DIA;
  const mostrarHoje = hoje >= 0 && hoje <= dias;

  return (
    <section>
      <Cabecalho titulo="Roadmap" sub={`${meses[0]} a ${meses[meses.length - 1]} · ${releases.length} release${releases.length === 1 ? "" : "s"}`}>
        {podePlanear && <button onClick={() => setNova(nova ? null : VAZIO)}>Nova release</button>}
      </Cabecalho>
      {erro && <p role="alert">{erro}</p>}
      {nova && (
        <form className="painel" onSubmit={criar}>
          <h2 className="titulo-fita">Nova release</h2>
          <label htmlFor="nome">Nome</label>
          <input id="nome" value={nova.nome} onChange={mudar("nome")} required />
          <label htmlFor="objetivo">Objetivo</label>
          <input id="objetivo" value={nova.objetivo} onChange={mudar("objetivo")} placeholder="por exemplo, avisos e filtros" />
          <div className="campos-lado">
            <div>
              <label htmlFor="inicio">Começa</label>
              <input id="inicio" type="date" value={nova.inicio} onChange={mudar("inicio")} required />
            </div>
            <div>
              <label htmlFor="prevista">Data prevista</label>
              <input id="prevista" type="date" value={nova.data_prevista} onChange={mudar("data_prevista")} required />
            </div>
          </div>
          <button type="submit">Criar release</button>
        </form>
      )}
      {releases.length === 0 ? (
        <p className="nota">Ainda não há releases.{podePlanear && " Cria a primeira em «Nova release»."}</p>
      ) : (
        <div className="painel roadmap">
          <div className="roadmap-meses">
            <span />
            {meses.map((m) => <span key={m} className="titulo-mao">{m}</span>)}
          </div>
          <div className="roadmap-corpo">
            {releases.map((r) => (
              <div key={r.id} className="roadmap-linha">
                <div className="roadmap-nome">
                  <strong>{r.nome}</strong>
                  <span className="suave">{ESTADOS_RELEASE[r.estado]} · {r.progresso}% concluído</span>
                  {r.em_risco && <span className="autocolante risco">Em risco</span>}
                </div>
                <div className="roadmap-pista">
                  <Link to="/roadmap/release" className={`fita-release ${r.estado}`} title={`${r.pedidos.length} pedido(s)`}
                    style={{ left: pos(dia(r.inicio)), width: pos(Math.max(dia(r.data_prevista) - dia(r.inicio), 1)) }}>
                    {r.objetivo || r.nome}
                  </Link>
                </div>
              </div>
            ))}
            {mostrarHoje && <span className="linha-hoje" style={{ left: `calc(var(--coluna-nomes) + (100% - var(--coluna-nomes)) * ${hoje / dias})` }}><em>hoje</em></span>}
          </div>
        </div>
      )}
      <p className="nota">Uma release fica em risco quando faltam duas semanas ou menos para a data prevista e ainda tem pedidos por concluir.</p>
    </section>
  );
}
