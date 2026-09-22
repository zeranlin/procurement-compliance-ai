.PHONY: validate structure contracts baseline-preflight baseline-smoke gate-b-model-smoke

validate: structure contracts
	@python3 scripts/detect_leakage.py

structure:
	@python3 scripts/validate_structure.py

contracts:
	@python3 scripts/validate_contracts.py

baseline-preflight:
	@python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1/C1_01_Preflight_Check_V0.2.1.py \
		--manifest contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1/C1_01_Baseline_Protocol_V0.2.1.lock.json --smoke

baseline-smoke:
	@python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1/harness.py smoke \
		--manifest contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1/C1_01_Baseline_Protocol_V0.2.1.lock.json \
		--adapter-command "python3 contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1/adapter_stub.py"

gate-b-model-smoke:
	@python3 scripts/gate_b_model_smoke.py \
		--output contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/reports/C1_01_Gate_B_Model_Smoke_V0.1.json
