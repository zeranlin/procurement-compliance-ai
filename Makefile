.PHONY: validate structure contracts

validate: structure contracts
	@python3 scripts/detect_leakage.py

structure:
	@python3 scripts/validate_structure.py

contracts:
	@python3 scripts/validate_contracts.py
