PYTHON ?= python

.PHONY: install test check demo demo-fraud demo-astronomy ablation serve

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) -m compileall -q src tests scripts experiments
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) -m quasar_engine.cli.main demo --domain all --points 360 --seed 42

demo-fraud:
	$(PYTHON) -m quasar_engine.cli.main demo --domain fraud --points 360 --seed 42

demo-astronomy:
	$(PYTHON) -m quasar_engine.cli.main demo --domain astronomy --points 360 --seed 42

ablation:
	$(PYTHON) scripts/run_ablation.py --domain all --points 360 --seed 42

serve:
	$(PYTHON) -m quasar_engine.cli.main serve --host 127.0.0.1 --port 8000

