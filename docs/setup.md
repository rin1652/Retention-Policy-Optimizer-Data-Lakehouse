# Setup và kiểm tra fixture — issue #2

Issue: [#2](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/2). Dùng [contract v1.0](experiment-contract.md) và [config chuẩn](../configs/experiment.sample.json).

## Môi trường thống nhất

- Python **3.12.x**; môi trường đã kiểm chứng dùng **3.12.6** trên Windows x64.
- NumPy **2.5.3**, pin trong `requirements.txt`.
- Test bằng `unittest` của Python, không cần thêm test framework.
- `.python-version` ghi minor version của dự án; kiểm tra `python --version` vì file này không tự đổi Python đang chạy.

## Windows PowerShell

Nếu chưa có repo:

```powershell
git clone https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse.git
cd Retention-Policy-Optimizer-Data-Lakehouse
```

Từ **root repo**, xác nhận Python 3.12 rồi tạo môi trường:

```powershell
python --version
python -m venv .venv
& "./.venv/Scripts/python.exe" -m pip install -r requirements.txt
& "./.venv/Scripts/python.exe" -c "import sys, numpy, src; print(sys.version); print(numpy.__version__); print('imports OK')"
```

Nếu `python` không trỏ tới 3.12, dùng `py -3.12 -m venv .venv` khi đã cài Python 3.12. Gọi Python trong venv trực tiếp nên không cần activate hoặc thay PowerShell ExecutionPolicy.

Chạy kiểm tra:

```powershell
& "./.venv/Scripts/python.exe" tools/validate_experiment_contract.py
& "./.venv/Scripts/python.exe" -m src.fixture_contract
& "./.venv/Scripts/python.exe" -m unittest discover -s tests -v
```

Kết quả nghiệm thu: contract **27 điều kiện đạt**, CLI fixture báo **7 incident thuộc 3 profile**, unittest **26 test đạt**. Khi thêm test về sau, số lượng có thể tăng; trạng thái kiểm tra vẫn phải thành công.

## Linux/macOS

Các lệnh sau dùng Python 3.12; việc nghiệm thu hiện tại thực hiện trên Windows, chưa xác minh các hệ điều hành này.

```sh
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python tools/validate_experiment_contract.py
./.venv/bin/python -m src.fixture_contract
./.venv/bin/python -m unittest discover -s tests -v
```

## Cấu trúc và cách import

```text
src/__init__.py                          package dùng chung
src/fixture_contract.py                  đọc/kiểm tra schema fixture
configs/experiment.sample.json           cấu hình chuẩn 810 GB
tests/fixtures/incidents.sample.jsonl     đầu vào 7 incident thủ công
tests/fixtures/expected.sample.json       đáp án tính tay, tách khỏi đầu vào
tests/test_fixture_contract.py           kiểm tra schema và đáp án
reports/.gitkeep                         giữ thư mục output trong Git
tools/validate_experiment_contract.py     kiểm tra đặc tả issue #1
```

Chạy từ root repo để `import src` hoạt động. Khi triển khai #5, Long thêm `src/generator.py`; các module khác dùng `from src.generator import generate_incidents`. Issue #2 chỉ cung cấp package và kiểm tra fixture, chưa có generator/evaluator/LLM/report thực.

## Fixture và ý nghĩa đáp án

Fixture dùng field `infrastructure_lost`, `anchor_gap_days`, `detect_delay_days`, `response_lag_days`, `target_age_days`, cùng table_id theo contract. ID có đủ split/scenario/seed/profile và số thứ tự. Validator kiểm tra `H=A+D+L` với sai số tuyệt đối tối đa `1e-9` ngày; quy tắc recovery `H<=TTL` vẫn giữ boundary bao gồm theo contract.

Các dòng này có split `development`, scenario `S1_infra_loss`, seed 1001 để dùng metadata hợp lệ. Tuy nhiên đây là bộ kiểm tra thủ công, không được xem là một dataset sinh đúng phân phối S1: không kiểm tra tỷ lệ hạ tầng 8% hoặc tổng 900 incident ở fixture nhỏ.

| Policy trong expected | TTL raw/curated/training | Cost | Đáp án |
|---|---|---:|---|
| minimum_valid | 1/7/14 | 83 GB | 4/7 tổng; 4/6 logical-only |
| uniform_baseline | 30/30/30 | 810 GB | 6/7 tổng; 6/6 logical-only |
| budget_invalid | 90/90/90 | 2430 GB | Invalid do vượt budget; không có coverage hợp lệ |
| minimum_invalid | 1/7/7 | 69 GB | Invalid do training TTL dưới 14 |

Expected là oracle tính tay, không phải kết quả nghiên cứu. Test kiểm tra cả đáp án lẫn các input lỗi: trường thiếu/thừa, ground truth trộn vào đầu vào, sai split/scenario/seed, tuổi âm/NaN/vô hạn/overflow, H không khớp và ID trùng. Evaluator ở #7 có thể dùng cùng fixture để kiểm tra implementation riêng.

## Kiểm tra tái lập bằng môi trường thứ hai

Tạo venv mới, không dùng system site-packages:

```powershell
python -m venv .venv-check
& "./.venv-check/Scripts/python.exe" -m pip install -r requirements.txt
& "./.venv-check/Scripts/python.exe" tools/validate_experiment_contract.py
& "./.venv-check/Scripts/python.exe" -m src.fixture_contract
& "./.venv-check/Scripts/python.exe" -m unittest discover -s tests -v
```

Môi trường `.venv-check` đã được đưa vào gitignore. Bằng chứng cài lại và nghiệm thu nằm trong [issue-02-review.md](issue-02-review.md).

## Cấu hình LLM và output

`.env.example` chỉ chứa tên biến `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` với giá trị trống. Key thật đặt trong môi trường riêng; `.env`/`.env.*` được bỏ qua bởi Git. Việc tạo `.env` chưa tự nạp biến vào Python; client/cách nạp sẽ làm ở #9. Issue #2 không yêu cầu credential hoặc gọi LLM.

Report sinh tự động được bỏ qua trong `reports/`, ngoại trừ `.gitkeep`. Khi có kết quả thật ở #13/#16, nhóm lưu evidence đã chọn vào thư mục được theo dõi hoặc đính kèm artifact và ghi đường dẫn trong issue. Giữ raw metrics để đối chiếu HTML/nhận xét LLM.

## Khi gặp lỗi

- **Sai version Python:** kiểm tra executable tạo venv, dùng Python 3.12; giữ đồng nhất minor version trong nhóm.
- **Không import được NumPy:** cài requirements bằng đúng Python trong venv, không cài vào Python khác.
- **Không import được src:** chuyển về root repo trước khi chạy; không chạy lệnh từ bên trong `src/`.
- **Fixture lỗi:** CLI trả exit code 2 và vị trí/lý do; sửa dữ liệu theo contract, không bỏ dòng sai âm thầm.
- **Lỗi network khi cài:** xử lý quyền mạng/proxy hoặc cài wheel tương thích được cung cấp; chỉ ghi nhận môi trường tái lập sau khi cài và kiểm tra thành công.
