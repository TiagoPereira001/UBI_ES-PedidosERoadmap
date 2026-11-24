import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import DetalhePedido from "../paginas/DetalhePedido.jsx";

afterEach(cleanup);

const PEDIDO = {
  id: 1,
  titulo: "Exportar em PDF",
  descricao: "Para a direção.",
  categoria_nome: "Relatórios",
  estado: "novo",
  estado_nome: "Novo",
  autor: "sofia",
  criado_em: "2026-11-01T10:00:00Z",
  total_votos: 0,
  votei: false,
  etiquetas: [],
  historico: [],
  pode_mudar_para: [],
  pode_editar: true,
};

const VERSOES = [
  {
    id: 10,
    titulo: "Exportar em PDF",
    descricao: "Texto original.",
    autor: "sofia",
    quando: "2026-11-01T10:00:00Z",
  },
  {
    id: 11,
    titulo: "Exportar em Excel",
    descricao: "Texto novo.",
    autor: "sofia",
    quando: "2026-11-02T11:00:00Z",
  },
];

function abrir({ pedido = PEDIDO, versoes = VERSOES, falhaEditar = null } = {}) {
  const fetchFalso = vi.fn(async (url, opcoes = {}) => {
    const caminho = url.replace(/^\/api/, "").split("?")[0];
    const metodo = (opcoes.method || "GET").toUpperCase();

    if (caminho === "/pedidos/1/" && metodo === "GET") {
      return { ok: true, status: 200, json: async () => pedido };
    }
    if (caminho === "/pedidos/1/" && metodo === "PATCH") {
      if (falhaEditar) {
        return { ok: false, status: falhaEditar.estado, json: async () => falhaEditar.dados };
      }
      const corpo = JSON.parse(opcoes.body);
      return {
        ok: true,
        status: 200,
        json: async () => ({ ...pedido, titulo: corpo.titulo, descricao: corpo.descricao }),
      };
    }
    if (caminho === "/pedidos/1/versoes/") {
      return { ok: true, status: 200, json: async () => versoes };
    }
    if (caminho === "/colaboracao/pedidos/1/comentarios/" || caminho === "/colaboracao/pessoas/") {
      return { ok: true, status: 200, json: async () => [] };
    }
    return { ok: false, status: 404, json: async () => ({}) };
  });
  globalThis.fetch = fetchFalso;
  render(
    <MemoryRouter initialEntries={["/pedidos/1"]}>
      <Routes>
        <Route path="/pedidos/:id" element={<DetalhePedido utilizador={{ username: "sofia", papel: "cliente" }} />} />
      </Routes>
    </MemoryRouter>,
  );
  return fetchFalso;
}

describe("versões do pedido (US-03)", () => {
  it("o botão Editar aparece com pode_editar e desaparece sem ele", async () => {
    abrir();
    expect(await screen.findByRole("button", { name: "Editar" })).toBeTruthy();
    cleanup();
    abrir({ pedido: { ...PEDIDO, pode_editar: false }, versoes: [] });
    expect(await screen.findByText("Para a direção.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Editar" })).toBeNull();
  });

  it("editar chama a API e mostra o formulário com rótulos", async () => {
    const fetchFalso = abrir();
    fireEvent.click(await screen.findByRole("button", { name: "Editar" }));
    expect(screen.getByLabelText("Título")).toBeTruthy();
    expect(screen.getByLabelText("Descrição")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Título"), { target: { value: "Novo título longo" } });
    fireEvent.change(screen.getByLabelText("Descrição"), { target: { value: "Nova descrição." } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    await waitFor(() => {
      const patch = fetchFalso.mock.calls.find(
        ([url, op]) => String(url).includes("/pedidos/1/") && op?.method === "PATCH",
      );
      expect(patch).toBeTruthy();
      expect(JSON.parse(patch[1].body)).toEqual({
        titulo: "Novo título longo",
        descricao: "Nova descrição.",
      });
    });
  });

  it("comparar mostra os dois textos", async () => {
    abrir();
    expect(await screen.findByText(/Versão 1 · sofia/)).toBeTruthy();
    fireEvent.click(screen.getByLabelText("Escolher versão 1"));
    fireEvent.click(screen.getByLabelText("Escolher versão 2"));
    expect(await screen.findByText("Texto original.")).toBeTruthy();
    expect(screen.getByText("Texto novo.")).toBeTruthy();
  });

  it("o erro do servidor aparece", async () => {
    abrir({ falhaEditar: { estado: 400, dados: { erro: "O título e a descrição não podem ficar vazios." } } });
    fireEvent.click(await screen.findByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Título"), { target: { value: "   " } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByText("O título e a descrição não podem ficar vazios.")).toBeTruthy();
  });
});
