PYTHON ?= python

.PHONY: install test check demo demo-fraud demo-astronomy benchmark ablation calibration scale serve

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
	$(PYTHON) -m quasar_engine.cli.main ablate --domain all --points 360 --seed 42

benchmark:
	$(PYTHON) -m quasar_engine.cli.main benchmark --domain all --points 360 --seeds 30

calibration:
	$(PYTHON) -m quasar_engine.cli.main calibrate --domain all --points 360 --seed 42

scale:
	$(PYTHON) -m quasar_engine.cli.main scale --domain fraud --sizes 1000,10000 --repeats 3

serve:
	$(PYTHON) -m quasar_engine.cli.main serve --host 127.0.0.1 --port 8000
