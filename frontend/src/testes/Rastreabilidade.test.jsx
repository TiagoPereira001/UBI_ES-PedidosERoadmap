import { afterEach, describe, expect, it } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Rastreabilidade from "../paginas/Rastreabilidade.jsx";
import { simularApi } from "./simular.js";

afterEach(cleanup);

const LINHAS = [
  {
    id: 3, titulo: "Exportação em PDF", autor: "sofia", estado: "concluido", estado_nome: "Concluído", sprint: "Sprint 4", equipa: "Equipa A", releases: ["Release 1.0"], falta: [],
    historias: [{
      id: 9, texto: "Como cliente, quero exportar.", criterios: [{ id: 1, texto: "Abre", cumprido: true }, { id: 2, texto: "Imprime", cumprido: false }],
      ligacoes: [{ id: 5, url: "https://github.com/x/commit/abc", descricao: "Exportação", criada_por: "diogo" }],
    }],
  },
  { id: 4, titulo: "Modo escuro", autor: "sofia", estado: "aprovado", estado_nome: "Aprovado", sprint: null, equipa: null, releases: [], historias: [], falta: ["Sem user stories"] },
];

function abrir(papel, extra = {}) {
  const fetchFalso = simularApi({ "/requisitos/rastreabilidade/": LINHAS, "/requisitos/criterios/2/": {}, ...extra });
  render(<MemoryRouter><Rastreabilidade utilizador={{ papel }} /></MemoryRouter>);
  return fetchFalso;
}

describe("rastreabilidade", () => {
  it("mostra a cadeia e o que falta ligar", async () => {
    abrir("gestor_projeto");
    expect(await screen.findByText("1 de 2 critérios cumpridos")).toBeTruthy();
    expect(screen.getByText("Sprint 4 · Equipa A · Release 1.0")).toBeTruthy();
    expect(screen.getByText("Sem user stories")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Exportação" }).getAttribute("href")).toBe("https://github.com/x/commit/abc");
    expect(screen.getByRole("checkbox", { name: "Imprime" }).disabled).toBe(true);
    expect(screen.queryByRole("button", { name: "Ligar" })).toBeNull();
  });

  it("a partir do commit chega-se ao pedido", async () => {
    abrir("gestor_projeto");
    fireEvent.change(await screen.findByRole("searchbox"), { target: { value: "commit/ABC" } });
    expect(screen.getByRole("link", { name: "Exportação em PDF" })).toBeTruthy();
    expect(screen.queryByText("Modo escuro")).toBeNull();
  });

  it("filtra o que falta", async () => {
    abrir("gestor_projeto");
    fireEvent.click(await screen.findByRole("checkbox", { name: "Só o que falta ligar" }));
    expect(screen.queryByText("Exportação em PDF")).toBeNull();
    expect(screen.getByText("Modo escuro")).toBeTruthy();
  });

  it("o Product Owner marca um critério", async () => {
    const fetchFalso = abrir("product_owner");
    fireEvent.click(await screen.findByRole("checkbox", { name: "Imprime" }));
    await screen.findByText("1 de 2 critérios cumpridos");
    const envio = fetchFalso.mock.calls.find(([url, o]) => url.includes("/criterios/2/") && o?.method === "PATCH");
    expect(JSON.parse(envio[1].body)).toEqual({ cumprido: true });
  });

  it("se o servidor recusar a ligação, o erro aparece e o texto não se perde", async () => {
    abrir("programador");
    fireEvent.change(await screen.findByLabelText("Endereço do commit"), { target: { value: "https://x.pt" } });
    fireEvent.change(screen.getByLabelText("O que foi feito"), { target: { value: "Teste" } });
    fireEvent.click(screen.getByRole("button", { name: "Ligar" }));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByLabelText("O que foi feito").value).toBe("Teste");
  });
});
