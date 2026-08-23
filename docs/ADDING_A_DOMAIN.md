# Como adicionar um domínio

## 1. Defina a pergunta

Escreva qual evento futuro é previsto, qual horizonte é legítimo e qual decisão humana será apoiada. Não comece pelas features.

## 2. Copie o template

Use `src/quasar_engine/adapters/template/adapter.py`. O adapter deve converter cada registro em `Observation` sem importar módulos internos do detector.

## 3. Mapeie os campos

- `timestamp`: momento real da observação;
- `source_id`: fluxo/sensor/sistema que compartilha background;
- `entity_id`: entidade opcional;
- `features`: somente números finitos nesta POC;
- `relations`: relações conhecidas opcionais;
- `context`: metadados não usados como rótulo oculto;
- `target_future`: rótulo opcional, exclusivo de avaliação.

## 4. Valide o arquivo

```bash
quasar validate-data --input observations.jsonl
```

## 5. Execute sem rótulos primeiro

```bash
quasar run --input observations.jsonl --output-dir runs/my_domain
```

## 6. Registre o experimento

Adicione configuração, versão/checksum do dataset, seed, horizonte, baselines, métricas e critérios de interrupção em `experiments/`.

## 7. Teste independência do core

O novo adapter pode fazer feature engineering específico, mas não deve duplicar `core/`. Se a matemática precisa mudar, trate isso como nova hipótese e execute ablation nos domínios anteriores.

