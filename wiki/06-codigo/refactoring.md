# Refactoring

[Índice](../README.md) · [← Testes](testes.md) · [Git e versões](git.md)

No EDS-192, reorganizámos regras repetidas sem alterar respostas da API nem regras do produto.

| Antes | Depois | Porquê | Testes |
|---|---|---|---|
| Cada API convertia `SemPermissao` e `RegraViolada` para HTTP à sua maneira. | `config/erros.py` centraliza a conversão: 403 e 400, respetivamente; as outras exceções seguem para o DRF. | Um único ponto mantém o mesmo JSON de erro e reduz tratamentos repetidos. | `config/tests/test_erros.py`: códigos, mensagem, delegação ao DRF e rollback de uma operação atómica. |
| Backlog, requisitos e roadmap repetiam verificações de papel; colaboração repetia a verificação ao gerir membros. | `pedidos.servicos.exigir_papel` concentra a regra e recebe os papéis permitidos e a mensagem. | Evita cópias e mantém as mensagens específicas de cada operação. | `pedidos/tests/test_servicos.py`, `backlog/tests/test_servicos.py`, `requisitos/tests/test_servicos.py`, `roadmap/tests/test_servicos.py` e `colaboracao/tests/test_equipas.py`. |
| Três operações da release repetiam a recusa quando já estava lançada. | `roadmap.servicos.exigir_release_nao_lancada` aplica a mesma guarda ao pôr, tirar e lançar. | A regra e a mensagem ficam num só sítio. | `roadmap/tests/test_servicos.py`: pôr e tirar numa release lançada, sem alterar os pedidos associados. |
