import { afterEach, describe, expect, it } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import EspacoEquipa from "../paginas/EspacoEquipa.jsx";
import { simularApi } from "./simular.js";

afterEach(cleanup);

const espaco = (extra = {}) => ({
  equipa: { id: 1, nome: "Equipa A" },
  membros: [{ id: 4, username: "diogo", papel: "programador", papel_nome: "Programador" }],
  trabalho: [{ pedido: 5, titulo: "Aviso por email", estado: "aprovado", estado_nome: "Aprovado", sprint: "Sprint 4" }],
  mensagens: [{ id: 1, autor: "diogo", texto: "Pego no aviso por email.", criada_em: new Date().toISOString() }],
  pode_escrever: false,
  pode_gerir: false,
  ...extra,
});

function abrir(papel, dados) {
  const fetchFalso = simularApi({
    "/backlog/equipas/": [{ id: 1, nome: "Equipa A" }],
    "/colaboracao/equipas/1/": dados,
    "/colaboracao/equipas/1/mensagens/": dados,
    "/colaboracao/equipas/1/membros/": dados,
    "/colaboracao/pessoas/": ["diogo", "ricardo", "sofia"],
  });
  render(<MemoryRouter><EspacoEquipa utilizador={{ username: "x", papel }} /></MemoryRouter>);
  return fetchFalso;
}

describe("espaço da equipa", () => {
  it("mostra quem somos, o trabalho e a conversa", async () => {
    abrir("cliente", espaco());
    expect(await screen.findByRole("heading", { name: "Equipa A" })).toBeTruthy();
    expect(screen.getByText("Aviso por email")).toBeTruthy();
    expect(screen.getByText("Pego no aviso por email.")).toBeTruthy();
    expect(screen.getByText(/Só os membros da equipa/)).toBeTruthy();
    expect(screen.queryByLabelText("Mensagem")).toBeNull();
  });

  it("um membro escreve na conversa", async () => {
    const fetchFalso = abrir("programador", espaco({ pode_escrever: true }));
    fireEvent.change(await screen.findByLabelText("Mensagem"), { target: { value: "Já está em revisão." } });
    fireEvent.click(screen.getByRole("button", { name: "Enviar" }));
    await screen.findByRole("heading", { name: "Equipa A" });
    const envio = fetchFalso.mock.calls.find(([url, o]) => url.includes("/mensagens/") && o?.method === "POST");
    expect(JSON.parse(envio[1].body)).toEqual({ texto: "Já está em revisão." });
  });

  it("a Helena junta pessoas que ainda não estão na equipa", async () => {
    const fetchFalso = abrir("gestor_projeto", espaco({ pode_escrever: true, pode_gerir: true }));
    const escolha = await screen.findByLabelText("Pessoa a juntar");
    expect(await screen.findByRole("option", { name: "ricardo" })).toBeTruthy();
    expect(screen.queryByRole("option", { name: "diogo" })).toBeNull();
    fireEvent.change(escolha, { target: { value: "ricardo" } });
    fireEvent.click(screen.getByRole("button", { name: "Juntar à equipa" }));
    await screen.findByRole("heading", { name: "Equipa A" });
    const envio = fetchFalso.mock.calls.find(([url, o]) => url.includes("/membros/") && o?.method === "POST");
    expect(JSON.parse(envio[1].body)).toEqual({ utilizador: "ricardo" });
  });
});
