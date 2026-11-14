import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ESTADOS } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";
import Icone from "../componentes/Icone.jsx";
import { quando } from "../componentes/formatos.js";

const SEMANA = 7 * 24 * 60 * 60 * 1000;

// Exporta a lista que está no ecrã, com os filtros aplicados, para abrir no Excel.
function exportar(pedidos) {
  const linhas = [["Pedido", "Categoria", "Etiquetas", "Estado", "Votos", "Atualizado"]];
  for (const p of pedidos) {
    linhas.push([p.titulo, p.categoria_nome, (p.etiquetas || []).join(" "), p.estado_nome, p.total_votos, p.atualizado_em || p.criado_em]);
  }
  const csv = linhas.map((l) => l.map((v) => `"${String(v ?? "").replaceAll('"', '""')}"`).join(";")).join("\n");
  const ligacao = document.createElement("a");
  ligacao.href = URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" }));
  ligacao.download = "pedidos.csv";
  ligacao.click();
  URL.revokeObjectURL(ligacao.href);
}

// Ecrã 02. Pesquisa e filtros juntos (US-04). Os filtros ficam no endereço, para se poder partilhar.
export default function Pedidos({ utilizador }) {
  const [params, setParams] = useSearchParams();
  const [resposta, setResposta] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [etiquetas, setEtiquetas] = useState([]);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.categorias().then(setCategorias).catch(() => {});
    api.etiquetas().then(setEtiquetas).catch(() => {});
  }, []);

  useEffect(() => {
    api
      .pedidos(Object.fromEntries(params))
      .then(setResposta)
      .catch(() => setErro("Não foi possível carregar os pedidos."));
  }, [params]);

  function filtrar(campo, valor) {
    const novo = new URLSearchParams(params);
    valor ? novo.set(campo, valor) : novo.delete(campo);
    setParams(novo);
  }

  const pedidos = resposta?.results;
  const total = resposta?.count ?? pedidos?.length ?? 0;
  const novos = (pedidos || []).filter((p) => p.criado_em && Date.now() - new Date(p.criado_em) < SEMANA).length;

  return (
    <section>
      <Cabecalho titulo="Pedidos" sub={pedidos ? `${total} pedidos · ${novos} novos esta semana` : " "}>
        <button className="secundario" onClick={() => exportar(pedidos || [])} disabled={!pedidos?.length}>Exportar</button>
        <Link className="botao" to="/pedidos/novo">Novo pedido</Link>
      </Cabecalho>

      <div className="barra-filtros">
        <div className="pesquisa">
          <Icone nome="procurar" tamanho={18} />
          <label htmlFor="q" className="so-leitor">Pesquisar</label>
          <input id="q" placeholder="Pesquisar no título ou na descrição" defaultValue={params.get("q") || ""}
            onKeyDown={(e) => e.key === "Enter" && filtrar("q", e.target.value)} />
        </div>
        <label htmlFor="estado" className="so-leitor">Estado</label>
        <select id="estado" className="filtro" value={params.get("estado") || ""} onChange={(e) => filtrar("estado", e.target.value)}>
          <option value="">Estado</option>
          {Object.entries(ESTADOS).map(([v, n]) => <option key={v} value={v}>{n}</option>)}
        </select>
        <label htmlFor="categoria" className="so-leitor">Categoria</label>
        <select id="categoria" className="filtro" value={params.get("categoria") || ""} onChange={(e) => filtrar("categoria", e.target.value)}>
          <option value="">Categoria</option>
          {categorias.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <label htmlFor="etiqueta" className="so-leitor">Etiqueta</label>
        <select id="etiqueta" className="filtro" value={params.get("etiqueta") || ""} onChange={(e) => filtrar("etiqueta", e.target.value)}>
          <option value="">Etiqueta</option>
          {etiquetas.map((nome) => <option key={nome} value={nome}>{nome}</option>)}
        </select>
        {utilizador && (
          <label className="opcao">
            <input type="checkbox" checked={params.get("meus") === "1"} onChange={(e) => filtrar("meus", e.target.checked ? "1" : "")} />
            Só os meus pedidos
          </label>
        )}
        <div className="ordenar">
          <label htmlFor="ordem">Ordenar por:</label>
          <select id="ordem" value={params.get("ordem") || ""} onChange={(e) => filtrar("ordem", e.target.value)}>
            <option value="">mais recentes</option>
            <option value="votos">mais votados</option>
          </select>
        </div>
      </div>

      {erro && <p role="alert">{erro}</p>}
      {pedidos && pedidos.length === 0 && (
        <div className="painel vazio">
          <p>Não há pedidos com estes filtros.</p>
          <button className="secundario" onClick={() => setParams({})}>Limpar filtros</button>
        </div>
      )}
      {pedidos && pedidos.length > 0 && (
        <>
          <div className="painel tabela-painel">
            <table>
              <thead>
                <tr><th>Pedido</th><th>Estado</th><th>Votos</th><th>Atualizado</th></tr>
              </thead>
              <tbody>
                {pedidos.map((p) => (
                  <tr key={p.id} className={p.estado === "rejeitado" ? "rejeitado" : undefined}>
                    <td>
                      <Link className="titulo-pedido" to={`/pedidos/${p.id}`}>{p.titulo}</Link>
                      <div className="meta-pedido">
                        <span>#{p.id} · {p.categoria_nome}</span>
                        {(p.etiquetas || []).map((e) => <span key={e} className="etiqueta">{e}</span>)}
                      </div>
                    </td>
                    <td><span className={`estado estado-${p.estado}`}>{p.estado_nome}</span></td>
                    <td className="votos">{p.total_votos}</td>
                    <td className="suave">{quando(p.atualizado_em || p.criado_em)} · {p.autor}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="nota">A mostrar {pedidos.length} de {total}.</p>
        </>
      )}
    </section>
  );
}
