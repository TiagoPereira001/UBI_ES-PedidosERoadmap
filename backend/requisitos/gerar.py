"""Propostas de user stories a partir de um pedido (US-18).

Há duas formas de fazer as propostas, como na sugestão de prioridade (decisões D4 e D8):

- um serviço de IA (Gemini ou Claude), através de `ia.cliente`, quando há uma chave configurada;
- um modelo local, sem rede, que monta as frases a partir do título e da descrição do pedido.

As propostas são só propostas: nada fica guardado sem o Product Owner aceitar.
"""

import logging
import re

from contas.models import Papel
from ia import cliente as servico_ia
from ia.erros import RespostaInvalida, SemIA

logger = logging.getLogger(__name__)

INSTRUCOES = (
    "És o analista de requisitos de uma equipa de produto. Recebes um pedido de funcionalidade em JSON "
    "(título, descrição, categoria e o papel de quem pediu). Escreve entre uma e três user stories em "
    "português de Portugal, cada uma no formato 'Como <papel>, quero <o quê>, para <porquê>.', e para cada "
    "uma entre dois e quatro critérios de aceitação curtos e verificáveis. Usa só o que está no pedido: não "
    "inventes números, prazos nem nomes de pessoas."
)

ESQUEMA = {
    "type": "object",
    "properties": {
        "historias": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string"},
                    "criterios": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["texto", "criterios"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["historias"],
    "additionalProperties": False,
}

PAPEIS = {
    Papel.CLIENTE: "cliente",
    Papel.PRODUCT_MANAGER: "product manager",
    Papel.PRODUCT_OWNER: "Product Owner",
    Papel.PROGRAMADOR: "programador",
    Papel.GESTOR_PROJETO: "gestor de projeto",
}

MAX_HISTORIAS = 5
MAX_CRITERIOS = 6


def _minuscula(texto):
    return texto[:1].lower() + texto[1:] if texto else texto


def _porque(descricao):
    """O 'para quê' do pedido: o que vem depois de ' para ' na descrição, se houver."""
    encontrado = re.search(r"\bpara (.+?)[.!?]?$", descricao.strip().split("\n")[0])
    return encontrado.group(1).strip() if encontrado else "não ter de o fazer à mão"


def propor_local(pedido):
    """Duas propostas montadas a partir do pedido: a do pedido em si e a do aviso a quem o pediu."""
    papel = PAPEIS.get(pedido.autor.papel, "utilizador")
    quero = _minuscula(pedido.titulo.strip().rstrip("."))
    return [
        {
            "texto": f"Como {papel}, quero {quero}, para {_porque(pedido.descricao)}.",
            "criterios": [
                f"Quem tem permissão consegue {quero}",
                "Quem não tem permissão não vê esta opção",
                "Fica registado no histórico do pedido",
            ],
        },
        {
            "texto": f"Como {papel}, quero ser avisado quando «{pedido.titulo.strip()}» estiver disponível, "
            "para começar a usá-lo.",
            "criterios": [
                "Quem pediu ou votou recebe uma notificação quando o pedido passa a Concluído",
                "A notificação diz o nome do pedido",
            ],
        },
    ]


def _validar(dados):
    historias = dados.get("historias") if isinstance(dados, dict) else None
    if not historias or len(historias) > MAX_HISTORIAS:
        raise RespostaInvalida("A IA não devolveu entre uma e cinco user stories.")
    limpas = []
    for h in historias:
        texto = str(h.get("texto", "")).strip()
        criterios = [str(c).strip() for c in h.get("criterios", []) if str(c).strip()]
        if not texto.startswith("Como ") or not criterios or len(criterios) > MAX_CRITERIOS:
            raise RespostaInvalida("A IA devolveu uma user story fora do formato.")
        limpas.append({"texto": texto, "criterios": criterios})
    return limpas


def propor(pedido):
    """Devolve (propostas, fonte, serviço). A fonte é 'ia' ou 'modelo local'; o serviço, 'gemini', 'claude' ou None."""
    dados = {
        "titulo": pedido.titulo,
        "descricao": pedido.descricao,
        "categoria": pedido.categoria.nome,
        "papel_de_quem_pediu": PAPEIS.get(pedido.autor.papel, "utilizador"),
    }
    try:
        resposta, servico = servico_ia.pedir_json(INSTRUCOES, dados, ESQUEMA)
        return _validar(resposta), "ia", servico
    except SemIA:
        pass
    except Exception:  # noqa: BLE001 - qualquer falha da IA leva ao modelo local
        logger.warning("A geração de user stories pela IA falhou; usei o modelo local.", exc_info=True)
    return propor_local(pedido), "modelo local", None
