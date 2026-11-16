import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "../api.js";

// A única porta para o servidor: manda o token CSRF, envia JSON e devolve os erros com os dados do servidor.
function responder(estado, corpo) {
  const fetchFalso = vi.fn(async () => ({ ok: estado < 400, status: estado, json: async () => corpo }));
  globalThis.fetch = fetchFalso;
  return fetchFalso;
}

afterEach(() => { document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT"; });

describe("api", () => {
  it("manda o token CSRF do cookie e o corpo em JSON", async () => {
    document.cookie = "csrftoken=abc123";
    const fetchFalso = responder(201, { id: 9 });
    expect(await api.criarPedido({ titulo: "Exportar" })).toEqual({ id: 9 });
    const [url, opcoes] = fetchFalso.mock.calls[0];
    expect(url).toBe("/api/pedidos/");
    expect(opcoes.method).toBe("POST");
    expect(opcoes.credentials).toBe("same-origin");
    expect(opcoes.headers["X-CSRFToken"]).toBe("abc123");
    expect(JSON.parse(opcoes.body)).toEqual({ titulo: "Exportar" });
  });

  it("os filtros vão no endereço e um GET não leva corpo", async () => {
    const fetchFalso = responder(200, []);
    await api.pedidos({ q: "relatórios", estado: "aprovado" });
    const [url, opcoes] = fetchFalso.mock.calls[0];
    expect(url).toBe("/api/pedidos/?q=relat%C3%B3rios&estado=aprovado");
    expect(opcoes.method).toBe("GET");
    expect(opcoes.body).toBeUndefined();
  });

  it("um erro traz o estado e a mensagem do servidor", async () => {
    responder(403, { erro: "Só o Product Owner pode ordenar." });
    const falha = await api.ordenar({ ids: [1] }).catch((e) => e);
    expect(falha.estado).toBe(403);
    expect(falha.dados.erro).toBe("Só o Product Owner pode ordenar.");
  });

  it("204 (sem conteúdo) devolve null", async () => {
    globalThis.fetch = vi.fn(async () => ({ ok: true, status: 204, json: async () => { throw new Error("sem corpo"); } }));
    expect(await api.apagarComentario(3)).toBeNull();
  });

  it("nenhum pedido da aplicação vai para fora do nosso servidor", async () => {
    const fetchFalso = responder(200, {});
    await Promise.all([api.sugestao(), api.notificacoes(), api.backlog(), api.eu()]);
    for (const [url] of fetchFalso.mock.calls) expect(url.startsWith("/api/")).toBe(true);
  });
});
