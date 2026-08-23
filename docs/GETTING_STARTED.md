# Guia de início

## Pré-requisitos

- Python 3.11, 3.12 ou 3.13;
- aproximadamente 200 MB livres para ambiente e dependências;
- nenhum banco, chave de API, GPU ou serviço cloud.

## Instalação no Windows

Abra o PowerShell dentro da pasta do projeto:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests -v
quasar demo --domain all --points 360 --seed 42
```

Se a execução de scripts do PowerShell bloquear a ativação, use temporariamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Instalação no Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests -v
quasar demo --domain all --points 360 --seed 42
```

## Comandos

| Comando | Finalidade |
|---|---|
| `quasar demo --domain all` | Executa os dois experimentos sintéticos |
| `quasar demo --domain fraud` | Executa apenas fraude/surveillance |
| `quasar demo --domain astronomy` | Executa apenas astronomia |
| `quasar show-config` | Mostra a configuração resolvida |
| `quasar validate-data --input FILE` | Valida JSONL próprio sem executar o core |
| `quasar run --input FILE` | Executa o core sobre o contrato comum |
| `quasar serve` | Inicia a API opcional, se instalada |

## Diagnóstico rápido

- `No module named quasar_engine`: confirme que o ambiente está ativado e execute `python -m pip install -e .`.
- `No module named numpy/pydantic/yaml`: execute `python -m pip install -r requirements/base.txt`.
- Poucos ou nenhum candidato: use ao menos 100 pontos; o background precisa de warm-up.
- Métricas diferentes: confirme seed, versão Python, arquivo de configuração e versão do pacote no `run_manifest.json`.

