# Bàn giao cost, baseline và generator MVP

Codex thực hiện phần tiếp theo của Thành (#4/#6) và Long (#5) theo yêu cầu người dùng. Kiểm tra kỹ thuật bởi Codex; không ghi Phúc/Long/Đức đã tự chạy hoặc phê duyệt.

## Đã có

- `src/cost_model.py`: cost history overhead, kiểm tra minimum/grid/budget và input sai. Invalid policy không được coi là kết quả hợp lệ.
- `src/policies.py`: baseline chung chỉ đọc config; ở 810 GB chọn TTL 30/30/30, cost 810. Budget 300 không có baseline uniform dù vector riêng 1/7/14 vẫn khả thi.
- `src/generator.py`: RNG theo SeedSequence seed/scenario-index/profile-index, mỗi dataset 900 incident. S1 có đúng 24 incident mất hạ tầng/profile; S0 không có.
- `src/config.py`: đọc config chung, kiểm tra mô hình hỗ trợ và hash theo contract. Không thêm profile/scenario config trùng lặp.

NumPy được pin lại **2.5.3** để giữ version RNG đã kiểm chứng; các dependency LLM Phúc bổ sung được giữ. Test phần này dùng Python 3.12.6/NumPy 2.5.3; chưa kiểm tra client/credential LLM.

## Dữ liệu và policy bàn giao

- [S0 development1001](../data/mvp/development/development-S0_main-s1001.jsonl) và [manifest](../data/mvp/development/manifest.json).
- [S0 holdout2001](../data/mvp/holdout/holdout-S0_main-s2001.jsonl) và [manifest](../data/mvp/holdout/manifest.json).
- [Baseline 810 GB](../data/mvp/baseline.json).

Manifest lưu SHA256 dataset, hash config, version và thống kê từng profile. Dữ liệu sinh có seed khác nhau, không trùng ID. Không dùng holdout/statistics của nó để chọn TTL.

Sampling v1.0: một RNG độc lập/profile; lấy A, D, L rồi chọn vị trí infrastructure-loss không hoàn lại. Mixture chọn component ngẫu nhiên cho từng incident, sau đó uniform theo thứ tự component; tỷ lệ component không bị ép chính xác. Index scenario/profile lấy theo thứ tự trong config. Cùng config/seed/version cho cùng byte JSONL.

## Kiểm tra đã chạy

**45/45 test đạt** (13 test mới + 32 test hiện có của fixture/evaluator), **27/27 kiểm tra contract đạt**. Đáp án cost tay 83/760/810/2430 GB, policy invalid, baseline/infeasible, tái lập seed, S0/S1, boundary và tích hợp evaluator hiện có đều được kiểm tra. [Log thực](evidence/mvp-components.json).

```powershell
& "./.venv/Scripts/python.exe" -m unittest discover -s tests -v
& "./.venv/Scripts/python.exe" tools/validate_experiment_contract.py
& "./.venv/Scripts/python.exe" -m src.cost_model
& "./.venv/Scripts/python.exe" -m src.policies --budget 810
```

Sinh lại vào **thư mục mới**, không ghi đè dữ liệu cũ:

```powershell
& "./.venv/Scripts/python.exe" -m src.generator --split development --scenario S0_main --seed 1001 --output-dir reports/dev-demo
& "./.venv/Scripts/python.exe" -m src.generator --split holdout --scenario S0_main --seed 2001 --output-dir reports/holdout-demo
```

Nếu đường dẫn đã tồn tại, chọn tên mới. Default của generator là S0 development1001; config vẫn là experiment.sample.json. S1 dùng cùng API với scenario S1_infra_loss. CLI hỗ trợ các dataset khác để mở rộng sau, nhưng không bắt buộc cho MVP.

## Việc tiếp theo

Thành làm #8 grid search rồi #12 ghép pipeline; Phúc hoàn thiện #9 LLM; Đức làm #10 HTML và tích hợp evaluator đã có ở src/evaluate.py. Long làm #11 failure case và #15 chạy lại sau khi có pipeline. Chưa có optimizer, eval so sánh holdout hoặc HTML/LLM thật trong bàn giao này.
