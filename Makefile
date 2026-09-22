.PHONY: validate structure contracts baseline-preflight baseline-smoke

validate: structure contracts
	@python3 scripts/detect_leakage.py

structure:
	@python3 scripts/validate_structure.py

contracts:
	@python3 scripts/validate_contracts.py

baseline-preflight:
	@python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness.py preflight \
		--input contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/fixtures/C1_01_Baseline_Smoke_Input_V0.2.jsonl --smoke

baseline-smoke:
	@python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness.py run \
		--input contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/fixtures/C1_01_Baseline_Smoke_Input_V0.2.jsonl \
		--adapter-command "python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/adapter_stub.py" \
		--model-id STUB --model-revision interface-only \
		--output /tmp/c1_01_smoke_predictions.jsonl --manifest /tmp/c1_01_smoke_manifest.json --smoke
