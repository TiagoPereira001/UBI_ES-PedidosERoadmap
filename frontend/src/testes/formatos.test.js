import { describe, expect, it } from "vitest";
import { iniciais, nomeDoPapel, quando } from "../componentes/formatos.js";

describe("formatos", () => {
  it("iniciais: duas letras do nome ou do nome e apelido", () => {
    expect(iniciais("sofia")).toBe("SO");
    expect(iniciais("Diogo Martins")).toBe("DM");
    expect(iniciais("Ana Maria Sousa")).toBe("AS");
    expect(iniciais("")).toBe("");
  });

  it("nome do papel, e o próprio valor se não o conhecer", () => {
    expect(nomeDoPapel("product_owner")).toBe("Product Owner");
    expect(nomeDoPapel("gestor_projeto")).toBe("Gestor de projeto");
    expect(nomeDoPapel("outro")).toBe("outro");
  });

  it("quando: hoje, ontem ou o dia e o mês", () => {
    const agora = new Date(2026, 10, 16, 15, 0);
    expect(quando(new Date(2026, 10, 16, 8, 0), agora)).toBe("hoje");
    expect(quando(new Date(2026, 10, 15, 23, 0), agora)).toBe("ontem");
    expect(quando(new Date(2026, 10, 2, 10, 0), agora)).toBe("02/11");
  });
});
