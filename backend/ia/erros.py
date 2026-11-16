class SemIA(Exception):
    """Não há nenhum serviço de IA configurado (falta a chave)."""


class RespostaInvalida(Exception):
    """O serviço de IA respondeu, mas não com o que pedimos."""
