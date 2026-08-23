# Limitações e riscos

## Científicos

- Dados sintéticos podem favorecer a forma dos detectores.
- Histograma em janelas pequenas introduz variância em entropia e informação mútua.
- Temperature scaling minimiza log-loss, não garante ECE menor em toda amostra.
- Coverage conformal é marginal e finita; não garante cobertura condicional por subgrupo.
- Lead time depende da definição do início do evento e do horizonte.
- Pesos e threshold ainda não têm intervalo de confiança entre seeds.

## De engenharia

- Estado vive em memória e reinicia com o processo.
- Não há tratamento específico para missing data além da validação de features presentes.
- Não há controle de concorrência, autenticação, rate limit ou fila.
- O endpoint opcional processa lotes e não implementa idempotência.
- O benchmark atual é local e não cobre alta cardinalidade de fontes.

## De uso

- Não usar para bloquear transações, diagnosticar saúde, operar mercado ou publicar descoberta científica sem validação independente e controles adequados.
- Um score alto é candidato estatístico, não explicação causal.
- Não conectar um LLM com poder decisório antes de preservar o protocolo de evidência e rejeição.

## Licenciamento e novidade

Apache-2.0 disciplina o uso do código, mas não prova originalidade, liberdade de operação ou patenteabilidade. Faça revisão de literatura, busca de anterioridade e aconselhamento jurídico antes de afirmações públicas.

