# Experimentos

## A - Fraude/surveillance sintética

Features: valor logarítmico, velocidade, risco da contraparte e densidade de rede. Três episódios são injetados com precursores distribuídos. O objetivo é testar combinação de sinais; não simular fielmente um banco.

```bash
quasar demo --domain fraud --points 360 --seed 42
```

## B - Astronomia sintética

Features: fluxo, índice de cor, largura espectral e background local. Três transientes sintéticos têm precursores moderados. O objetivo é testar transferência do core; não descobrir um objeto real.

```bash
quasar demo --domain astronomy --points 360 --seed 42
```

## Partições

Depois do warm-up, a sequência pontuada é separada cronologicamente:

- passado inicial: operação/background;
- 20%: calibração de temperatura e resíduos conformais;
- 25% finais: teste held-out.

## Reprodutibilidade

Não altere seed ou pesos depois de olhar apenas o resultado final. Se explorar configurações, registre cada tentativa e separe um novo teste final. O `run_manifest.json` contém hash da configuração e ambiente.

## Interpretação dos artefatos

`predictions.jsonl` é a trilha principal. Ele registra partição, probabilidade bruta, probabilidade calibrada, intervalo, métricas de evidência e rótulo revelado. `candidates.jsonl` contém somente pontos acima do threshold; não deve substituir a avaliação de todas as previsões.

