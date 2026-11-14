import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";

// Ecrã 01. Uma ficha presa ao quadro com fita-cola. Quem se regista fica como cliente;
// os outros papéis atribui-os um administrador.
export default function Entrar({ aoEntrar }) {
  const [modo, setModo] = useState("entrar");
  const [dados, setDados] = useState({ username: "", email: "", password: "" });
  const [erro, setErro] = useState("");
  const navegar = useNavigate();
  const entrar = modo === "entrar";

  const mudar = (campo) => (e) => setDados({ ...dados, [campo]: e.target.value });

  async function enviar(e) {
    e.preventDefault();
    setErro("");
    try {
      const u = entrar ? await api.entrar(dados.username, dados.password) : await api.registar(dados);
      aoEntrar(u);
      navegar("/pedidos");
    } catch (falha) {
      setErro(falha.dados?.erro || "Não foi possível. Confirma os dados.");
    }
  }

  return (
    <div className="ecra-entrar">
      <form className="ficha-entrar" onSubmit={enviar}>
        <span className="fita-cola" aria-hidden="true" />
        <h1>{entrar ? "Entrar no quadro" : "Criar conta"}</h1>
        <label htmlFor="u">Utilizador</label>
        <input id="u" value={dados.username} onChange={mudar("username")} autoComplete="username" required />
        {!entrar && (
          <>
            <label htmlFor="e">Email</label>
            <input id="e" type="email" value={dados.email} onChange={mudar("email")} placeholder="nome@empresa.pt" />
          </>
        )}
        <label htmlFor="p">Palavra-passe</label>
        <input id="p" type="password" value={dados.password} onChange={mudar("password")}
          autoComplete={entrar ? "current-password" : "new-password"} required />
        {erro && <p role="alert">{erro}</p>}
        <button type="submit" className="largo">{entrar ? "Entrar" : "Criar conta"}</button>
      </form>
      <aside className="ao-lado">
        <div className="postit">
          <p>{entrar ? "Primeira vez aqui? Regista-te: começas como cliente e o administrador dá-te o papel na equipa." : "Já tens conta? Entra com o teu utilizador."}</p>
        </div>
        <button type="button" className="secundario" onClick={() => setModo(entrar ? "registar" : "entrar")}>
          {entrar ? "Criar conta" : "Entrar"}
        </button>
      </aside>
    </div>
  );
}
