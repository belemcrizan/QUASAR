# Referência da API Python

## Uso mínimo

```python
from quasar_engine import DiscoveryPipeline, Observation

observations = [
    Observation(
        timestamp="2026-08-23T14:30:00Z",
        source_id="sensor_A",
        entity_id="entity_42",
        features={"signal_a": 1.4, "signal_b": 0.32},
        context={"domain": "example"},
    )
]

output = DiscoveryPipeline().process(observations)
```

O pipeline precisa de warm-up; uma única observação não gera forecast.

## Objetos públicos

- `Observation`: contrato de entrada.
- `Relation`: relação opcional entre entidades.
- `Candidate` e `Evidence`: candidato rastreável.
- `Hypothesis`: afirmação estrutural, evidências e critério de rejeição.
- `Forecast`: probabilidade, intervalo e horizonte.
- `PipelineConfig`: configuração tipada.
- `DiscoveryPipeline`: orquestrador local stateful.
- `PipelineOutput`: observações pontuadas, candidatos e hipóteses.

## Configuração por YAML

```python
from quasar_engine import DiscoveryPipeline, PipelineConfig

config = PipelineConfig.from_yaml("configs/base.yaml")
pipeline = DiscoveryPipeline(config)
```

## REST opcional

`POST /detect` recebe `{"observations": [...]}` e cria um pipeline novo por requisição. Isso evita estado compartilhado na POC, mas não é uma arquitetura de streaming. `GET /health` retorna status e versão.

