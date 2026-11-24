import { afterEach, describe, expect, it } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Roadmap, { janela } from "../paginas/Roadmap.jsx";
import { simularApi } from "./simular.js";

afterEach(cleanup);

const release = (id, nome, extra = {}) => ({
  id, nome, objetivo: "", inicio: "2026-11-02", data_prevista: "2026-11-27", lancada_em: null,
  estado: "em_curso", progresso: 0, em_risco: false, pedidos: [], milestones: [], ...extra,
});
const ROADMAP = {
  releases: [
    release(1, "Release 1.0", {
      objetivo: "Avisos e filtros",
      em_risco: true,
      milestones: [{ id: 1, nome: "Beta para clientes", data: "2026-11-15", estado: "por_comecar" }],
    }),
    release(2, "Release 2.0", { inicio: "2026-11-30", data_prevista: "2026-12-18", estado: "planeada" }),
  ],
};

function abrir(papel) {
  const fetchFalso = simularApi({ "/roadmap/": ROADMAP });
  render(<MemoryRouter><Roadmap utilizador={{ username: "x", papel }} /></MemoryRouter>);
  return fetchFalso;
}

describe("roadmap", () => {
  it("mostra as releases e marca a que está em risco (Helena)", async () => {
    abrir("gestor_projeto");
    expect(await screen.findByText("Release 1.0")).toBeTruthy();
    expect(screen.getByText("Avisos e filtros")).toBeTruthy();
    expect(screen.getByText(/Beta para clientes/)).toBeTruthy();
    expect(screen.getAllByText("Em risco")).toHaveLength(1);
    expect(screen.queryByRole("button", { name: "Nova release" })).toBeNull();
  });

  it("a Marta cria uma release com nome e datas", async () => {
    const fetchFalso = abrir("product_manager");
    fireEvent.click(await screen.findByRole("button", { name: "Nova release" }));
    fireEvent.change(screen.getByLabelText("Nome"), { target: { value: "Release 3.0" } });
    fireEvent.change(screen.getByLabelText("Começa"), { target: { value: "2027-01-04" } });
    fireEvent.change(screen.getByLabelText("Data prevista"), { target: { value: "2027-01-29" } });
    fireEvent.click(screen.getByRole("button", { name: "Criar release" }));
    await screen.findByText("Release 1.0");
    const envio = fetchFalso.mock.calls.find(([, opcoes]) => opcoes?.method === "POST");
    expect(JSON.parse(envio[1].body)).toMatchObject({ nome: "Release 3.0", inicio: "2027-01-04", data_prevista: "2027-01-29" });
  });

  it("a janela tem quatro meses a partir da primeira release", () => {
    const { meses } = janela(ROADMAP.releases);
    expect(meses).toEqual(["Novembro", "Dezembro", "Janeiro", "Fevereiro"]);
  });
});
