PY := .venv/bin/python
EB := .venv/bin/ebench

.PHONY: setup test dry-run report clean-dry

setup:            ## create venv and install pinned deps
	uv venv --python 3.12 .venv
	uv pip install --python $(PY) -r requirements.txt
	uv pip install --python $(PY) -e . --no-deps

test:             ## run unit tests (free, no network)
	$(PY) -m pytest -q

dry-run: clean-dry ## full pipeline with the mock client (free); starts from scratch
	$(EB) run --dry-run --run-id dryrun-local --tickets tests/fixtures/sample_tickets.jsonl --max-usd 1
	$(EB) score --run-id dryrun-local
	$(EB) judge --run-id dryrun-local --dry-run --max-usd 1 --tickets tests/fixtures/sample_tickets.jsonl
	$(EB) export-labels --run-id dryrun-local --tickets tests/fixtures/sample_tickets.jsonl --splits test
	$(EB) report --run-id dryrun-local
	$(EB) power --run-id dryrun-local --n-tickets 70 --repeats 2

report:           ## regenerate ALL tables and figures from raw data (set RUN=<run_id>)
	$(EB) score --run-id $(RUN)
	$(EB) report --run-id $(RUN)

clean-dry:
	rm -rf runs/dryrun-* results/dryrun
