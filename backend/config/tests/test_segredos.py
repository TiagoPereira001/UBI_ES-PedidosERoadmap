"""As chaves de IA nunca vão para o repositório (wiki/04-arquitetura/ia.md).

A chave verdadeira fica só no ficheiro .env da raiz, que o Git ignora. O docker-compose.yml lê-a de lá
por variável. Estes testes falham se alguém colar uma chave num ficheiro que vai para o GitHub.
"""

import re
import subprocess
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

RAIZ = Path(settings.BASE_DIR).parent

# Formatos das chaves da Google (antigo e novo), da Anthropic e do LM Studio.
CHAVES = re.compile(
    r"AIza[0-9A-Za-z_\-]{35}|\bAQ\.[0-9A-Za-z_\-]{30,}|sk-ant-[0-9A-Za-z_\-]{20,}|sk-lm-[0-9A-Za-z_\-]{8,}"
)
VARIAVEIS = ["LMSTUDIO_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]


def ficheiros_no_git():
    """Os ficheiros que vão para o GitHub. Dentro do Docker não há Git nem a raiz do projeto, e o teste salta."""
    try:
        saida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        raise unittest.SkipTest("Sem o repositório Git à vista (por exemplo, dentro do contentor).") from None
    return [RAIZ / nome for nome in saida.stdout.decode().split("\0") if nome]


class SemChavesNoRepositorio(SimpleTestCase):
    def test_nenhum_ficheiro_do_git_tem_uma_chave(self):
        encontradas = []
        for ficheiro in ficheiros_no_git():
            try:
                texto = ficheiro.read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
                continue  # imagens e PDFs não são texto
            if CHAVES.search(texto):
                encontradas.append(str(ficheiro.relative_to(RAIZ)))
        self.assertEqual(encontradas, [], "Há uma chave de API num ficheiro que vai para o GitHub.")

    def test_o_env_nao_vai_para_o_git(self):
        nomes = {f.name for f in ficheiros_no_git()}
        self.assertNotIn(".env", nomes)
        self.assertIn(".env", (RAIZ / ".gitignore").read_text(encoding="utf-8").split())

    def test_o_compose_le_as_chaves_do_env_por_variavel(self):
        compose = RAIZ / "docker-compose.yml"
        if not compose.exists():
            self.skipTest("Sem o docker-compose.yml à vista (por exemplo, dentro do contentor).")
        texto = compose.read_text(encoding="utf-8")
        for nome in VARIAVEIS:
            with self.subTest(nome):
                self.assertRegex(texto, rf"\n\s+{nome}: \$\{{{nome}:-\}}\n")

    def test_o_modelo_do_env_nao_traz_chaves_preenchidas(self):
        exemplo = (Path(settings.BASE_DIR) / ".env.example").read_text(encoding="utf-8")
        for nome in VARIAVEIS:
            with self.subTest(nome):
                self.assertNotRegex(exemplo, rf"(?m)^{nome}=\S")
