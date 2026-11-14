import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App, { AREAS } from "../App.jsx";
import { simularApi } from "./simular.js";

afterEach(cleanup);

describe("menu", () => {
  it("tem as sete áreas dos mockups, as notificações e o Entrar", async () => {
    simularApi({ "/contas/eu/": { autenticado: false }, "/categorias/": [], "/pedidos/": { results: [] } });
    render(<MemoryRouter initialEntries={["/pedidos"]}><App /></MemoryRouter>);
    const areas = within(screen.getByRole("navigation"));
    for (const { area } of AREAS) {
      expect(areas.getAllByRole("link", { name: area }).length).toBeGreaterThan(0);
    }
    expect(areas.getByRole("link", { name: "Notificações" })).toBeTruthy();
    expect(await areas.findByRole("link", { name: "Entrar" })).toBeTruthy();
  });

  it("a área aberta mostra os ecrãs dela por baixo", async () => {
    simularApi({ "/contas/eu/": { autenticado: false } });
    render(<MemoryRouter initialEntries={["/dashboard"]}><App /></MemoryRouter>);
    const menu = within(screen.getByRole("navigation"));
    const [area] = menu.getAllByRole("link", { name: "Dashboard", current: "page" });
    expect(area.className).toBe("area ativa");
    expect(menu.getByRole("link", { name: "Carga das equipas" })).toBeTruthy();
    expect(menu.queryByRole("link", { name: "Novo pedido" })).toBeNull();
    expect(await menu.findByRole("link", { name: "Entrar" })).toBeTruthy();
  });

  it("os 15 ecrãs do Figma têm todos lugar", () => {
    const ecras = AREAS.flatMap((a) => a.ecras.map(([, nome]) => nome));
    // 12 nas áreas + Notificações + Entrar + Detalhe do pedido (abre a partir da lista) = os 15 ecrãs do Figma
    expect(ecras.length + 3).toBe(15);
  });

  it("com conta, mostra quantas notificações estão por ler", async () => {
    simularApi({
      "/contas/eu/": { autenticado: true, utilizador: { username: "sofia", papel: "cliente" } },
      "/colaboracao/notificacoes/": { por_ler: 3, itens: [] },
      "/categorias/": [], "/etiquetas/": [], "/pedidos/": { results: [] },
    });
    render(<MemoryRouter><App /></MemoryRouter>);
    expect(await screen.findByText("3")).toBeTruthy();
  });
});
