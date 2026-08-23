# Getting started

## Requirements

- Python 3.11, 3.12, or 3.13;
- no database, API key, GPU, or cloud service;
- approximately 200 MB for the environment and dependencies.

## Windows PowerShell

~~~powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m unittest discover -s tests -v
quasar demo --domain all --points 360 --seed 42
~~~

If OneDrive or antivirus makes environment creation unusually slow, create the environment outside the synchronized folder:

~~~powershell
$venv = "$env:LOCALAPPDATA\quasar-venv"
py -3.13 -m venv $venv
& "$venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
~~~

Wait until each command returns to the prompt before running the next one.

## Linux or macOS

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m unittest discover -s tests -v
quasar demo --domain all --points 360 --seed 42
~~~

## Command map

| Command | Purpose |
|---|---|
| quasar demo | Run one or both synthetic domains |
| quasar benchmark | Aggregate repeated seeds and 95% confidence intervals |
| quasar calibrate | Compare temperature, Platt, and isotonic calibration |
| quasar ablate | Remove evidence components under a fixed protocol |
| quasar scale | Measure local runtime, memory, and throughput |
| quasar prepare-data | Convert supported CSV datasets to Observation JSONL |
| quasar validate-data | Validate Observation JSONL |
| quasar run | Score arbitrary Observation JSONL without labels |
| quasar evaluate-data | Evaluate labeled Observation JSONL temporally |
| quasar show-config | Print the resolved configuration |
| quasar serve | Start the optional local REST API |

## Fast troubleshooting

- Module not found: activate the environment and run python -m pip install -e .
- quasar command not found: check Get-Command quasar on Windows or which quasar on Unix.
- Too few scored observations: provide at least 100 rows and allow background warm-up.
- Different metrics: compare seed, package version, Python version, configuration hash, and platform in run_manifest.json.
- Large scale run refused: sizes above 100,000 require the explicit --confirm-large flag.

