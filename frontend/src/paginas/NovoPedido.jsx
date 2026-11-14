import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import Cabecalho from "../componentes/Cabecalho.jsx";

const QUEM_GERE = ["product_manager", "product_owner"];

// Ecrã 03. Título, descrição e uma só categoria (Sofia). Os parecidos aparecem enquanto
// se escreve o título, cada um com o seu botão de votar (US-05).
export default function NovoPedido({ utilizador }) {
  const [dados, setDados] = useState({ titulo: "", descricao: "", categoria: "", origem: "sistema" });
  const [etiquetas, setEtiquetas] = useState("");
  const [categorias, setCategorias] = useState([]);
  const [parecidos, setParecidos] = useState([]);
  const [erros, setErros] = useState({});
  const navegar = useNavigate();

  useEffect(() => {
    api.categorias().then(setCategorias).catch(() => {});
  }, []);

  useEffect(() => {
    if (dados.titulo.trim().length < 4) {
      setParecidos([]);
      return;
    }
    // Espera que a pessoa pare de escrever antes de perguntar ao servidor.
    const espera = setTimeout(() => {
      api.parecidos(dados.titulo).then(setParecidos).catch(() => setParecidos([]));
    }, 300);
    return () => clearTimeout(espera);
  }, [dados.titulo]);

  const mudar = (campo) => (e) => setDados({ ...dados, [campo]: e.target.value });

  async function votar(id) {
    const r = await api.votar(id);
    setParecidos(parecidos.map((p) => (p.id === id ? { ...p, total_votos: r.total_votos, votei: r.votei } : p)));
  }

  async function submeter(e) {
    e.preventDefault();
    try {
      const pedido = await api.criarPedido(dados);
      if (etiquetas.trim()) await api.classificar(pedido.id, { etiquetas: etiquetas.split(",") });
      navegar(`/pedidos/${pedido.id}`);
    } catch (falha) {
      setErros(falha.dados || { geral: "Não foi possível submeter." });
    }
  }

  if (!utilizador) {
    return (
      <section>
        <Cabecalho titulo="Novo pedido" sub="Conta o que precisas. O Product Owner lê todos os pedidos." />
        <p>Para submeter um pedido tens de <Link to="/entrar">entrar</Link>.</p>
      </section>
    );
  }

  const gere = QUEM_GERE.includes(utilizador.papel);

  return (
    <section>
      <Cabecalho titulo="Novo pedido" sub="Conta o que precisas. O Product Owner lê todos os pedidos." />
      <div className="grelha-lado">
        <form className="painel formulario" onSubmit={submeter}>
          <label htmlFor="titulo">Título</label>
          <input id="titulo" value={dados.titulo} onChange={mudar("titulo")} placeholder="Exportar relatórios para Excel" required />
          {erros.titulo && <p role="alert">{erros.titulo}</p>}
          <label htmlFor="descricao">Descrição</label>
          <textarea id="descricao" rows={4} value={dados.descricao} onChange={mudar("descricao")}
            placeholder="O que precisas e para quê." required />
          <div className="campos-lado">
            <div>
              <label htmlFor="categoria">Categoria</label>
              <select id="categoria" value={dados.categoria} onChange={mudar("categoria")} required>
                <option value="">Escolhe uma</option>
                {categorias.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
              </select>
            </div>
            {gere && (
              <div>
                <label htmlFor="etiquetas">Etiquetas (separadas por vírgulas)</label>
                <input id="etiquetas" value={etiquetas} onChange={(e) => setEtiquetas(e.target.value)} placeholder="excel, exportar" />
              </div>
            )}
          </div>
          {gere && (
            <>
              <label htmlFor="origem">Origem (quando registas em nome de alguém)</label>
              <select id="origem" value={dados.origem} onChange={mudar("origem")}>
                <option value="sistema">Sistema</option>
                <option value="email">Email</option>
                <option value="reuniao">Reunião</option>
                <option value="chat">Chat</option>
              </select>
            </>
          )}
          {erros.geral && <p role="alert">{erros.geral}</p>}
          <div className="botoes">
            <button type="submit">Submeter pedido</button>
            <Link className="botao secundario" to="/pedidos">Cancelar</Link>
          </div>
        </form>

        {parecidos.length > 0 && (
          <aside className="ao-lado" aria-label="Pedidos parecidos">
            <div className="postit">
              <p>Já existe? Vota nele em vez de criar outro.</p>
            </div>
            <ul className="parecidos">
              {parecidos.map((p) => (
                <li key={p.id} className="cartao-linha">
                  <Link to={`/pedidos/${p.id}`}>{p.titulo}</Link>
                  <span className="votos">{p.total_votos}</span>
                  <button type="button" className="secundario pequeno" onClick={() => votar(p.id)}>{p.votei ? "Retirar voto" : "Votar"}</button>
                </li>
              ))}
            </ul>
          </aside>
        )}
      </div>
    </section>
  );
}
