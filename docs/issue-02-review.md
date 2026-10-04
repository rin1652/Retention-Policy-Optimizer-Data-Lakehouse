# Issue #2 — Bàn giao phần Long và nghiệm thu kỹ thuật hộ Đức

Issue: [#2](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/2).  
Thời điểm nghiệm thu: **04/10/2026 17:10:29, giờ Việt Nam (UTC+7)**.  
Người thực hiện: **Codex**, theo yêu cầu người dùng làm thay phần Long và nghiệm thu hộ Đức. Không ghi Long hoặc Đức đã trực tiếp chạy hay xác nhận.

## Kết quả

**Đạt phạm vi issue #2:** môi trường, dependency cố định, package dùng chung, fixture/expected độc lập, kiểm tra schema và hướng dẫn tái lập.

| Hạng mục | Bằng chứng |
|---|---|
| Python / NumPy | Python 3.12.6, NumPy 2.5.3 |
| Cài đặt tái lập | Venv .venv-check mới, cài requirements, không dùng system site-packages |
| Package và dependency | Import src và numpy thành công |
| Contract v1.0 | 27/27 điều kiện đạt |
| Fixture | 7 incident, đủ 3 profile, đúng field/ID/H=A+D+L |
| Test | 26/26 test đạt trên venv chính và venv sạch |
| Expected tính tay | Policy 1/7/14: cost83, 4/7; baseline30: cost810, 6/7; invalid policy tách riêng |
| Dữ liệu lỗi | Thiếu/thừa field, boolean sai, tuổi âm/NaN/vô hạn/overflow, trùng ID, sai split/scenario/seed bị từ chối |
| Git hygiene | Venv, key và report sinh tự động bị ignore; .env.example và reports/.gitkeep được giữ |
| Tài liệu | docs/setup.md và README có lệnh cài/chạy kiểm tra |

## Lệnh nghiệm thu đã chạy

```powershell
python -m venv .venv-check
& "./.venv-check/Scripts/python.exe" -m pip install -r requirements.txt
& "./.venv-check/Scripts/python.exe" tools/validate_experiment_contract.py
& "./.venv-check/Scripts/python.exe" -m src.fixture_contract
& "./.venv-check/Scripts/python.exe" -m unittest discover -s tests -v
```

Chi tiết kết quả và log test: [evidence/issue-02-acceptance.json](evidence/issue-02-acceptance.json). Venv sạch được tạo riêng trên cùng máy Windows; installer dùng cached wheel của NumPy, không tái sử dụng package đã cài trong venv chính.

## Bàn giao cho các issue tiếp theo

- **Long/#5:** thêm generator thật trong src/generator.py, dùng config/scenario/RNG theo contract.
- **Thành/#4 và #6:** hiện thực cost/baseline; dùng expected fixture để kiểm tra kết quả độc lập.
- **Đức/#7:** hiện thực evaluator; dùng 7 incident để kiểm tra boundary, infra-loss và invalid policy trước dataset lớn.
- **Phúc/#3 và #9:** tiếp tục research và LLM; .env.example hiện chỉ mô tả tên biến, chưa có client hay cơ chế tự nạp .env.

## Giới hạn và ý nghĩa kết quả

Fixture được viết thủ công, không tuân tỷ lệ 8% hạ tầng/900 incident của dataset nghiên cứu. Các tỷ lệ 4/7, 6/7 là đáp án tính tay cho kiểm tra, không phải kết quả cải thiện metric.

Chưa chạy generator, optimizer, evaluator, LLM hoặc xuất report eval thực. Việc thêm validator fixture chỉ phục vụ tích hợp schema. Linux/macOS có lệnh tham khảo trong setup nhưng chưa được nghiệm thu. Cần kiểm tra các module thực trong issue của chúng.

