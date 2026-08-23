# Como contribuir

## Antes do código

Abra uma questão com hipótese, domínio, dados, métrica, baseline e risco de vazamento temporal. Mudanças que apenas melhoram um seed não devem entrar.

## Padrão local

```bash
python -m pip install -e ".[dev]"
python -m compileall -q src tests scripts experiments
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

## Regras

- preserve a API pública em `quasar_engine.__init__`;
- mantenha adapters fora do core;
- não use `target_future` em background, dinâmica, detector ou forecast;
- adicione teste para cada correção;
- fixe seed e registre configuração;
- reporte falhas e resultados negativos;
- não use linguagem causal sem desenho causal apropriado;
- dependências obrigatórias precisam de justificativa.

## Commits sugeridos

Use mensagens como `feat: add PELT baseline`, `fix: prevent temporal leakage` ou `docs: explain conformal coverage`.

