// Dados de exemplo dos ecrãs que ainda não falam com a API (ligam no Sprint 5).
// Os números são inventados para a demonstração; não são medições.

export function AvisoExemplo() {
  return <p className="nota exemplo">Ecrã com dados de exemplo. Liga à API no Sprint 5.</p>;
}

// Roadmap de outubro a janeiro: inicio e fim em dias desde 1 de outubro (o roadmap tem 123 dias).
export const MESES = ["Outubro", "Novembro", "Dezembro", "Janeiro"];
export const DIAS_NO_ROADMAP = 123;
export const RELEASES = [
  { nome: "Release 1.0", tema: "pedidos e votação", inicio: 2, fim: 42, marco: "Lançada", diaMarco: 40, estado: "lancada", progresso: 100 },
  { nome: "Release 2.0", tema: "exportar relatórios", inicio: 30, fim: 72, marco: "Beta a 15/11", diaMarco: 76, estado: "em_curso", progresso: 45, emRisco: true, contrato: true },
  { nome: "Release 3.0", tema: "dashboards", inicio: 63, fim: 108, estado: "planeada", progresso: 10 },
];

export const EQUIPAS = [
  { nome: "Equipa A", pessoas: ["Diogo Martins", "Ana Sousa"], capacidade: 10, novo: 6, manutencao: 2, bugs: 3, administrativo: 1 },
  { nome: "Equipa B", pessoas: ["Marta Lopes", "Helena Costa"], capacidade: 10, novo: 3, manutencao: 1, bugs: 1, administrativo: 1 },
  { nome: "Equipa C", pessoas: ["Ricardo Almeida"], capacidade: 10, novo: 2, manutencao: 0, bugs: 1, administrativo: 0 },
];
