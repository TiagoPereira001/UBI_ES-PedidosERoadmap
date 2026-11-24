// Pequenas regras de apresentação usadas em vários ecrãs.

const PAPEIS = {
  cliente: "Cliente",
  product_manager: "Product manager",
  product_owner: "Product Owner",
  programador: "Programador",
  gestor_projeto: "Gestor de projeto",
};

// Quem fez a sugestão da IA, com o nome que o servidor devolve em "servico".
export const SERVICOS_IA = {
  lmstudio: "Gemma 4 (local, no LM Studio)",
  gemini: "Gemini (Google)",
  claude: "Claude (Anthropic)",
};

export const nomeDoPapel = (papel) => PAPEIS[papel] || papel;

// Duas letras para o círculo de cada pessoa ("sofia" dá "SO", "Diogo Martins" dá "DM").
export function iniciais(nome = "") {
  const partes = nome.trim().split(/\s+/);
  const letras = partes.length > 1 ? partes[0][0] + partes[partes.length - 1][0] : nome.slice(0, 2);
  return letras.toUpperCase();
}

const DIA = 24 * 60 * 60 * 1000;

// "hoje", "ontem" ou o dia e o mês, como nas listas dos mockups.
export function quando(data, agora = new Date()) {
  const d = new Date(data);
  const dias = Math.floor((new Date(agora.toDateString()) - new Date(d.toDateString())) / DIA);
  if (dias <= 0) return "hoje";
  if (dias === 1) return "ontem";
  return d.toLocaleDateString("pt-PT", { day: "2-digit", month: "2-digit" });
}

export const diaMes = (data) => new Date(data).toLocaleDateString("pt-PT", { day: "2-digit", month: "2-digit" });
