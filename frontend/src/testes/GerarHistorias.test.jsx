import { afterEach, describe, expect, it } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import GerarHistorias from "../paginas/GerarHistorias.jsx";
import { simularApi } from "./simular.js";

afterEach(cleanup);

const PEDIDO = { id: 3, titulo: "Exportação em PDF", descricao: "Para mandar à direção.", estado: "aprovado", estado_nome: "Aprovado", total_historias: 1 };
const HISTORIAS = {
  pedido: PEDIDO,
  historias: [{ id: 9, texto: "Como cliente, quero exportar, para mandar à direção.", origem: "ia", origem_nome: "IA", aceite_por: "ricardo", criterios: [{ id: 1, texto: "Abre no leitor de PDF", cumprido: false }] }],
};
const PROPOSTAS = {
  fonte: "modelo local",
  servico: null,
  propostas: [{ texto: "Como cliente, quero ser avisado, para começar a usar.", criterios: ["Recebe a notificação"] }],
};

function abrir(papel) {
  const fetchFalso = simularApi({
    "/requisitos/pedidos/": [PEDIDO],
    "/requisitos/pedidos/3/historias/": HISTORIAS,
    "/requisitos/pedidos/3/propostas/": PROPOSTAS,
  });
  render(<MemoryRouter><GerarHistorias utilizador={{ username: "x", papel }} /></MemoryRouter>);
  return fetchFalso;
}

describe("gerar user stories", () => {
  it("mostra o pedido, as aceites e os critérios", async () => {
    abrir("programador");
    expect(await screen.findByText("Como cliente, quero exportar, para mandar à direção.")).toBeTruthy();
    expect(screen.getByText("Abre no leitor de PDF")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Gerar propostas" })).toBeNull();
  });

  it("o Ricardo gera propostas, vê de onde vieram e aceita", async () => {
    const fetchFalso = abrir("product_owner");
    fireEvent.click(await screen.findByRole("button", { name: "Gerar propostas" }));
    expect(await screen.findByText(/modelo local/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Texto da user story"), { target: { value: "Como cliente, quero ser avisado por email, para começar a usar." } });
    fireEvent.click(screen.getByRole("button", { name: "Aceitar" }));
    await screen.findByText(/aceite por ricardo/);
    const envio = fetchFalso.mock.calls.find(([url, o]) => url.includes("/historias/") && o?.method === "POST");
    expect(JSON.parse(envio[1].body)).toEqual({
      texto: "Como cliente, quero ser avisado por email, para começar a usar.", criterios: ["Recebe a notificação"], origem: "local",
    });
  });

  it("rejeitar tira a proposta sem a guardar", async () => {
    const fetchFalso = abrir("product_owner");
    fireEvent.click(await screen.findByRole("button", { name: "Gerar propostas" }));
    fireEvent.click(await screen.findByRole("button", { name: "Rejeitar" }));
    expect(screen.queryByText("Como cliente, quero ser avisado, para começar a usar.")).toBeNull();
    expect(fetchFalso.mock.calls.some(([url, o]) => url.includes("/historias/") && o?.method === "POST")).toBe(false);
  });
});
