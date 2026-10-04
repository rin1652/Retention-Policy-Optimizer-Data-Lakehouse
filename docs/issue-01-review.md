# Issue #1 — Nghiệm thu kỹ thuật contract v1.0

Issue: [#1](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1).  
Thời điểm kiểm tra: **04/10/2026 16:45:55, giờ Việt Nam (UTC+7)**.  
Người thực hiện: **Codex, theo yêu cầu người dùng hoàn thiện các điểm còn thiếu**.

## Phạm vi và kết luận

Contract/config đã được đồng bộ về cấu hình Phúc đưa lên repo: budget chính 810 GB, baseline 30 ngày, cùng grid [1,7,14,30,60,90]. Hoàn thiện routing development/holdout/shift, full config hash và run ID không ghi đè. Đây là nghiệm thu bước đặc tả của issue #1, không phải kết quả thí nghiệm của toàn dự án.

## Các điểm đã xử lý

| Điểm cần sửa | Kết quả |
| --- | --- |
| Hướng dẫn cũ 360 GB khác config repo | Contract/config 810 GB là nguồn chính; mô tả issue được thay bằng v1.0 |
| Seed và scenario chưa ghép rõ | S0/S1 học riêng; S2/S3 dùng policy S0 đã khóa; seed ghép theo k |
| Run ID có thể trùng cùng giây | UUID4 + tạo thư mục độc quyền + retry khi đụng tên |
| Thiếu bằng chứng kiểm tra | Script kiểm tra 27 điều kiện, kết quả passed |
| Review chưa ghi đúng trạng thái | Ghi review kỹ thuật do Codex thực hiện; không ghi Long/Đức đã xác nhận |

## Bằng chứng kiểm chứng

Chạy ở root repo bằng Python 3:

```text
python tools/validate_experiment_contract.py
```

Kết quả thực thi:

- **27/27 điều kiện đạt**.
- 216 candidate vector, 66 vector khả thi.
- Baseline TTL 30 ngày, cost 810 GB.
- Vector (14,60,90) cost 760 GB; minimum vector cost 83 GB.
- Kiểm tra boundary H=TTL, mất hạ tầng, vượt budget và minimum TTL.
- Kiểm tra seed không giao nhau, routing đủ 4 scenario và aggregate không trộn scenario.
- Ép một run ID đụng tên để xác nhận allocation tạo thư mục mới và giữ nội dung run cũ.
- Config SHA-256: `daa6825ef86ac612ff0bffed9e69ec69f6a7236e3ec079f174132513af022d4d`.

Chi tiết tên điều kiện:

- `contract_version_1.0`
- `three_unique_profiles`
- `positive_cost_and_minimum`
- `grid_sorted_unique_positive`
- `mixture_weights_and_bounds`
- `216_candidates_66_feasible`
- `baseline_30_days_810_GB`
- `fixture_cost_760_GB`
- `fixture_budget_violation`
- `fixture_minimum_violation`
- `minimum_vector_cost_83_GB`
- `budget_300_uniform_infeasible`
- `fixture_boundary_and_infrastructure`
- `900_incidents_and_24_infra_per_profile`
- `disjoint_seed_sets`
- `holdout_not_optimizer_input`
- `scenario_routing_exact`
- `seed_pairing_covers_all_runs`
- `aggregate_keeps_scenarios_separate`
- `forced_run_id_collision_preserves_old_run`
- `uuid_and_exclusive_allocation_declared`
- `contract_documents_810 GB`
- `contract_documents_66 vector`
- `contract_documents_S0 development`
- `contract_documents_UUID4`
- `contract_documents_evaluation_routing`
- `contract_documents_64 ký tự`

## Trạng thái xác nhận của thành viên

Nguyễn Đình Phúc đã đưa contract/config ban đầu vào repo trong commit `36d871d`. Người dùng giao Codex hoàn thiện và kiểm tra các điểm còn thiếu. Không có comment xác nhận độc lập của Long hoặc Đức tại thời điểm nghiệm thu; không đánh dấu hai người đã review. Thông tin này được ghi rõ khi bàn giao issue.

## Giới hạn

Chưa chạy generator/optimizer/evaluator thực, chưa có coverage đo từ simulation và chưa gọi LLM. Script chỉ kiểm chứng contract, config, fixture tính tay và mẫu allocation run ID. Code eval/report trong các issue sau phải áp dụng quy tắc đã chốt và được kiểm tra lại. Không tuyên bố quy tắc của mô phỏng là retention an toàn cho engine production.

