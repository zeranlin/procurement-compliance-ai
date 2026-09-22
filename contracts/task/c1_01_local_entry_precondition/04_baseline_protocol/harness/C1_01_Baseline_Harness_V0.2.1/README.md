# C1-01 Baseline Harness V0.2.1

`FROZEN` dependency-patch Protocol Integration package for `C1-01_LOCAL_ENTRY_PRECONDITION`.
It preserves `C1_01_Baseline_Protocol_V0.2` and rebinds only the MetricSpec
dependency to `C1_01_Benchmark_Metric_Spec_V0.2`.

## Commands

Run the protocol smoke suite with the deterministic stub:

```bash
python3 harness.py smoke \
  --manifest C1_01_Baseline_Protocol_V0.2.1.lock.json \
  --adapter-command "python3 adapter_stub.py"
```

Run a formal Base Model adapter only after the preflight inputs are complete:

```bash
python3 harness.py run \
  --manifest C1_01_Baseline_Protocol_V0.2.1.lock.json \
  --train train.jsonl --dev dev.jsonl --blind-input blind_test_input.jsonl \
  --adapter-command "python3 model_adapter.py" \
  --model-id BASE-MODEL-X --model-revision REVISION \
  --output baseline_predictions.jsonl \
  --run-manifest baseline_run_manifest.json
```

The preflight gate must pass before the adapter is called. Source-rework rows,
`target=null`, `HOLD`, `DISPUTED`, and `BLIND_GOLD` are refused as dataset
inputs. Invalid model output is retained as `INVALID` for scoring.

`adapter_stub.py` is for interface testing only. It is not a model baseline.
See `C1_01_Baseline_Protocol_V0.2.1.md` for the frozen contract and
`C1_01_Model_Output_Schema_V0.2.json` for the exact bare prediction object.

Run `python3 regression_tests.py` for the V0.2.1 dependency/preflight contract
regression. It uses synthetic contract fixtures only; it does not run a model,
DEV Benchmark, or Blind Test.
