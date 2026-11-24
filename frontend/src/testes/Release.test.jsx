import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import Release from "../paginas/Release.jsx";

afterEach(cleanup);

const RELEASE = {
  id: 2,
  nome: "Release 2.0",
  objetivo: "Integrações",
  inicio: "2026-11-30",
  data_prevista: "2026-12-18",
  lancada_em: null,
  estado: "planeada",
  progresso: 0,
  em_risco: false,
  pedidos: [
    { id: 3, titulo: "Ligação ao Slack", estado: "aprovado", estado_nome: "Aprovado" },
  ],
  milestones: [
    {
      id: 1,
      nome: "Beta",
      data: "2026-12-05",
      estado: "por_comecar",
      pedidos: [{ id: 3, titulo: "Ligação ao Slack", estado: "aprovado", estado_nome: "Aprovado" }],
    },
  ],
  dependencias: [
    {
      id: 1,
      pedido: 3,
      pedido_titulo: "Ligação ao Slack",
      depende_de: 4,
      depende_de_titulo: "Lista de pedidos mais rápida",
      criada_por: "diogo",
      criada_em: "2026-11-16T10:00:00Z",
    },
  ],
  avisos: [
    {
      pedido_id: 3,
      pedido_titulo: "Ligação ao Slack",
      depende_de_id: 4,
      depende_de_titulo: "Lista de pedidos mais rápida",
      mensagem: "Ligação ao Slack depende de Lista de pedidos mais rápida.",
    },
  ],
  aprovados: [
    { id: 3, titulo: "Ligação ao Slack" },
    { id: 5, titulo: "Aviso por email quando o pedido é lido" },
    { id: 4, titulo: "Lista de pedidos mais rápida" },
  ],
};

function abrir({ papel = "product_manager", release = RELEASE, falhaDependencia = null } = {}) {
  const fetchFalso = vi.fn(async (url, opcoes = {}) => {
    const caminho = url.replace(/^\/api/, "").split("?")[0];
    const metodo = (opcoes.method || "GET").toUpperCase();

    if (caminho === "/roadmap/releases/2/" && metodo === "GET") {
      return { ok: true, status: 200, json: async () => release };
    }
    if (caminho === "/roadmap/releases/2/" && metodo === "POST") {
      return { ok: true, status: 200, json: async () => ({ ...release, lancada_em: "2026-12-18" }) };
    }
    if (caminho === "/roadmap/dependencias/" && metodo === "POST") {
      if (falhaDependencia) {
        return { ok: false, status: 400, json: async () => falhaDependencia };
      }
      return { ok: true, status: 201, json: async () => ({ id: 9 }) };
    }
    if (caminho.startsWith("/roadmap/milestones/") && caminho.endsWith("/pedidos/") && metodo === "POST") {
      return { ok: true, status: 200, json: async () => release.milestones[0] };
    }
    if (caminho === "/roadmap/milestones/" && metodo === "POST") {
      return { ok: true, status: 201, json: async () => ({ id: 9, nome: "Lançamento", data: "2026-12-18", estado: "por_comecar", pedidos: [] }) };
    }
    return { ok: false, status: 404, json: async () => ({}) };
  });
  globalThis.fetch = fetchFalso;
  render(
    <MemoryRouter initialEntries={["/roadmap/releases/2"]}>
      <Routes>
        <Route path="/roadmap/releases/:id" element={<Release utilizador={{ username: "x", papel }} />} />
      </Routes>
    </MemoryRouter>,
  );
  return fetchFalso;
}

describe("release (ecrã 09)", () => {
  it("o select de acrescentar não mostra pedidos já na release", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Release 2.0" });
    const select = document.getElementById("pedido-release");
    const textos = [...select.options].map((o) => o.textContent);
    expect(textos).toContain("Aviso por email quando o pedido é lido");
    expect(textos).not.toContain("Ligação ao Slack");
  });

  it("erro de ciclo do servidor aparece em role=alert", async () => {
    abrir({
      falhaDependencia: { erro: "Essa dependência formaria um ciclo (direto ou indireto)." },
    });
    await screen.findByRole("heading", { name: "Release 2.0" });
    fireEvent.change(document.getElementById("dep-de"), { target: { value: "3" } });
    fireEvent.change(document.getElementById("dep-para"), { target: { value: "4" } });
    fireEvent.click(screen.getByRole("button", { name: "Adicionar dependência" }));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByText(/ciclo/)).toBeTruthy();
  });

  it("pôr pedido no milestone chama a API", async () => {
    const fetchFalso = abrir();
    await screen.findByRole("heading", { name: "Release 2.0" });
    fireEvent.change(screen.getByLabelText("Funcionalidade"), { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: "Pôr no milestone" }));
    await waitFor(() => {
      const envio = fetchFalso.mock.calls.find(
        ([url, op]) => String(url).includes("/roadmap/milestones/1/pedidos/") && op?.method === "POST",
      );
      expect(envio).toBeTruthy();
      expect(JSON.parse(envio[1].body)).toEqual({ pedido: 5 });
    });
  });

  it("o programador vê tudo mas só mexe nas dependências", async () => {
    abrir({ papel: "programador" });
    expect(await screen.findByText(/Ligação ao Slack → Lista/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Adicionar dependência" })).toBeTruthy();
    expect(screen.getByText("Beta")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Pôr no milestone" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Lançar release" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Novo milestone" })).toBeNull();
  });
});
