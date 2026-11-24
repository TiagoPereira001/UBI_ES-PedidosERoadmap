import { useEffect, useState } from "react";
import { Link, NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import Icone from "./componentes/Icone.jsx";
import { iniciais, nomeDoPapel } from "./componentes/formatos.js";
import { api } from "./api.js";
import Entrar from "./paginas/Entrar.jsx";
import Pedidos from "./paginas/Pedidos.jsx";
import NovoPedido from "./paginas/NovoPedido.jsx";
import DetalhePedido from "./paginas/DetalhePedido.jsx";
import Priorizacao from "./paginas/Priorizacao.jsx";
import PlanearSprint from "./paginas/PlanearSprint.jsx";
import QuadroSprint from "./paginas/QuadroSprint.jsx";
import Roadmap from "./paginas/Roadmap.jsx";
import Release from "./paginas/Release.jsx";
import GerarHistorias from "./paginas/GerarHistorias.jsx";
import Rastreabilidade from "./paginas/Rastreabilidade.jsx";
import Notificacoes from "./paginas/Notificacoes.jsx";
import EspacoEquipa from "./paginas/EspacoEquipa.jsx";
import Dashboard from "./paginas/Dashboard.jsx";
import CargaEquipas from "./paginas/CargaEquipas.jsx";

// O menu segue os mockups (Figma, Alta Fidelidade): uma entrada por área, com ícone. Os ecrãs de cada
// área aparecem por baixo dela quando se está lá. As notificações e quem está a usar ficam em baixo.
export const AREAS = [
  { area: "Pedidos", icone: "pedidos", ecras: [["/pedidos", "Pedidos"], ["/pedidos/novo", "Novo pedido"]] },
  { area: "Priorização", icone: "priorizacao", ecras: [["/priorizacao", "Priorização"]] },
  { area: "Backlog", icone: "backlog", ecras: [["/sprint/planear", "Planear sprint"], ["/sprint/quadro", "Quadro do sprint"]] },
  { area: "Roadmap", icone: "roadmap", ecras: [["/roadmap", "Roadmap"], ["/roadmap/release", "Release 2.0"]] },
  { area: "Requisitos", icone: "requisitos", ecras: [["/requisitos/gerar", "Gerar user stories"], ["/requisitos/rastreabilidade", "Rastreabilidade"]] },
  { area: "Equipa", icone: "equipa", ecras: [["/equipa", "Espaço da equipa"]] },
  { area: "Dashboard", icone: "dashboard", ecras: [["/dashboard", "Dashboard"], ["/dashboard/carga", "Carga das equipas"]] },
];

// Uma área está aberta quando o endereço é um dos seus ecrãs (o detalhe /pedidos/5 é da área Pedidos).
const PREFIXOS = { Pedidos: "/pedidos", Backlog: "/sprint", Roadmap: "/roadmap", Requisitos: "/requisitos", Dashboard: "/dashboard" };
const estaNaArea = (a, caminho) =>
  a.ecras.some(([c]) => c === caminho) || (PREFIXOS[a.area] && caminho.startsWith(PREFIXOS[a.area]));

export default function App() {
  const [utilizador, setUtilizador] = useState(null);
  const [porLer, setPorLer] = useState(0);
  const location = useLocation();

  useEffect(() => {
    api.eu().then((r) => setUtilizador(r.autenticado ? r.utilizador : null)).catch(() => {});
  }, []);

  // O número de notificações por ler (ecrã 12) atualiza-se a cada mudança de ecrã.
  useEffect(() => {
    if (!utilizador) return setPorLer(0);
    api.notificacoes().then((r) => setPorLer(r.por_ler)).catch(() => {});
  }, [utilizador, location.pathname]);

  async function sair() {
    await api.sair();
    setUtilizador(null);
  }

  // O ecrã 01 ocupa a página toda, sem o menu (como no mockup).
  if (location.pathname === "/entrar") {
    return <Entrar aoEntrar={setUtilizador} />;
  }

  return (
    <div className="aplicacao">
      <nav className="menu" aria-label="Áreas">
        <Link to="/pedidos" className="marca"><span className="marca-postit" aria-hidden="true" />Roadmap</Link>
        <ul className="areas">
          {AREAS.map((a) => {
            const aberta = estaNaArea(a, location.pathname);
            return (
              <li key={a.area}>
                <Link to={a.ecras[0][0]} className={aberta ? "area ativa" : "area"} aria-current={aberta ? "page" : undefined}>
                  <Icone nome={a.icone} />
                  {a.area}
                </Link>
                {aberta && a.ecras.length > 1 && (
                  <ul className="ecras-da-area">
                    {a.ecras.map(([caminho, nome]) => (
                      <li key={caminho}><NavLink to={caminho} end>{nome}</NavLink></li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
        <div className="rodape">
          <NavLink to="/notificacoes" className="area">
            <Icone nome="sino" />
            Notificações
            {porLer > 0 && <span className="contador" aria-label={`${porLer} por ler`}>{porLer}</span>}
          </NavLink>
          {utilizador ? (
            <div className="quem">
              <span className="avatar">{iniciais(utilizador.username)}</span>
              <div>
                <strong>{utilizador.username}</strong>
                <span>{nomeDoPapel(utilizador.papel)}</span>
              </div>
              <button className="so-icone" onClick={sair} aria-label="Sair" title="Sair"><Icone nome="sair" tamanho={18} /></button>
            </div>
          ) : (
            <Link to="/entrar" className="botao secundario">Entrar</Link>
          )}
        </div>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/pedidos" replace />} />
          <Route path="/pedidos" element={<Pedidos utilizador={utilizador} />} />
          <Route path="/pedidos/novo" element={<NovoPedido utilizador={utilizador} />} />
          <Route path="/pedidos/:id" element={<DetalhePedido utilizador={utilizador} />} />
          <Route path="/priorizacao" element={<Priorizacao utilizador={utilizador} />} />
          <Route path="/sprint/planear" element={<PlanearSprint utilizador={utilizador} />} />
          <Route path="/sprint/quadro" element={<QuadroSprint utilizador={utilizador} />} />
          <Route path="/roadmap" element={<Roadmap utilizador={utilizador} />} />
          <Route path="/roadmap/release" element={<Release />} />
          <Route path="/requisitos/gerar" element={<GerarHistorias />} />
          <Route path="/requisitos/rastreabilidade" element={<Rastreabilidade />} />
          <Route path="/notificacoes" element={<Notificacoes utilizador={utilizador} />} />
          <Route path="/equipa" element={<EspacoEquipa />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/carga" element={<CargaEquipas />} />
        </Routes>
      </main>
    </div>
  );
}
