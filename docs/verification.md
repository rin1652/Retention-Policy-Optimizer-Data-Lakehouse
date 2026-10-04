# Demo verification

Checked on 2026-10-04, branch `feature/task-07-10-hardening`, after merging `origin/main` at `788d42e`.

## Commands

```bash
python -m unittest discover -s tests -v
python tools/validate_experiment_contract.py
python -m src.main
cd front_end && npm ci && npm run build && npm run lint
```

## Results

- Python tests: PASS, 56/56.
- Experiment contract: PASS, 27/27.
- Frontend build/lint: PASS after `npm ci`.
- Pipeline generated separate report folders for each eval run; no overwrite observed.
- HTML contains the policy ids found in each run's `metrics.json`.
- LLM real commentary: FAIL in this environment because `FPT_API_KEY` is not configured. The report still writes an explicit LLM error status instead of failing the eval.

## Reproducibility check

Two consecutive `python -m src.main` executions produced matching metrics for the same config and seeds.

| Run | Scenario | Policy | Recoverable/Total | Coverage | Cost GB | Delta pp |
| --- | --- | --- | --- | --- | --- | --- |
| `20261004T181518-daa6825e-eb6ecc06939540e39b7aa56662e95392` | S0_main | baseline-S0_main-dev1001-B810 | 798/900 | 0.8866666667 | 810 | 11.3333333333 |
| `20261004T181518-daa6825e-eb6ecc06939540e39b7aa56662e95392` | S0_main | optimized-S0_main-dev1001-B810 | 900/900 | 1.0 | 410 | 11.3333333333 |
| `20261004T181521-daa6825e-3138751248d84e0e84a50d750d014cce` | S1_infra_loss | baseline-S1_infra_loss-dev1001-B810 | 749/900 | 0.8322222222 | 810 | 8.7777777778 |
| `20261004T181521-daa6825e-3138751248d84e0e84a50d750d014cce` | S1_infra_loss | optimized-S1_infra_loss-dev1001-B810 | 828/900 | 0.92 | 410 | 8.7777777778 |
| `20261004T181644-daa6825e-5606a2ed7f184e8c9bcacca249b1ba84` | S0_main | baseline-S0_main-dev1001-B810 | 798/900 | 0.8866666667 | 810 | 11.3333333333 |
| `20261004T181644-daa6825e-5606a2ed7f184e8c9bcacca249b1ba84` | S0_main | optimized-S0_main-dev1001-B810 | 900/900 | 1.0 | 410 | 11.3333333333 |
| `20261004T181648-daa6825e-b7159d576d284566afa7f54e91647fbd` | S1_infra_loss | baseline-S1_infra_loss-dev1001-B810 | 749/900 | 0.8322222222 | 810 | 8.7777777778 |
| `20261004T181648-daa6825e-b7159d576d284566afa7f54e91647fbd` | S1_infra_loss | optimized-S1_infra_loss-dev1001-B810 | 828/900 | 0.92 | 410 | 8.7777777778 |

## Remaining blocker


