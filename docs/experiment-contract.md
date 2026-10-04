# Experiment contract: Retention Policy Optimizer (TASK-01)

Phiên bản: 1.0-draft. Người phụ trách: Nguyễn Đình Phúc (`rin1652`). Người kiểm tra: Nguyễn Việt Thành.
Múi giờ mọi mốc: Asia/Ho_Chi_Minh (UTC+7). Lịch 05/10/2026 09:00 đến 09:10 là lịch tạm theo sprint 2 giờ, không phải deadline do giảng viên công bố.

Config mẫu đi kèm: [`configs/experiment.sample.json`](../configs/experiment.sample.json). Mọi giá trị số trong tài liệu này khớp với file đó. Khi hai nơi lệch nhau, sửa cả hai rồi tính lại config hash.

## 1. Giả thuyết và phạm vi

**H1 (giả thuyết chính).** Ở cùng history-overhead budget, TTL riêng theo profile bảng đạt RecoveryCoverage cao hơn TTL chung.

**H0.** Coverage của TTL riêng bằng hoặc thấp hơn TTL chung trên holdout. Kết quả này vẫn được báo cáo nguyên trạng nếu thí nghiệm công bằng.

Giả thuyết bổ sung: lợi ích giảm khi delay giữa các profile gần nhau hoặc khi phân phối holdout dịch chuyển mạnh (kiểm bằng scenario S2, S3).

Phạm vi và giới hạn cần giữ trong mọi tài liệu sau:

- Đây là mô phỏng Python với cost tuyến tính. TTL trong mô phỏng không phải cấu hình VACUUM hay expire snapshot cho production. Delta khuyến nghị khoảng giữ an toàn dài hơn transaction và stream lag dài nhất, nên giá trị 1 ngày của raw chỉ là ứng viên của mô phỏng lý tưởng.
- Time travel không phải backup. Sự cố mất hạ tầng (S1) là giới hạn mà retention không giải quyết được.
- Metric là RecoveryCoverage trên số sự cố, không trọng số theo criticality. Criticality chỉ đi vào qua `min_ttl_days`.

## 2. Đơn vị và quy ước

| Đại lượng | Đơn vị | Ghi chú |
| --- | --- | --- |
| Thời gian (TTL, A, D, L, H) | ngày, số thực | so sánh bằng float64, không làm tròn |
| Dung lượng | GB | cost lịch sử tăng thêm, không gồm current data |
| `history_gb_per_day` (h_i) | GB/ngày | file lịch sử phải giữ thêm mỗi ngày, không phải bytes ingest |
| Budget B | GB | trần history overhead, chính: 810 GB |

Cost model: `cost(v) = sum_i h_i * ttl_i`. Current data giống nhau giữa các policy nên không đưa vào cost. Không dùng ingest rate thay cho `h_i`.

## 3. Ba profile (đóng băng trước khi mở holdout)

| table_id | h_i (GB/ngày) | min TTL (ngày) | Criticality | Delay D (ngày) |
| --- | --- | --- | --- | --- |
| `raw_ingest` | 20 | 1 | medium | 90% U(0,2) + 10% U(2,7) |
| `curated_business` | 5 | 7 | high | 80% U(0,7) + 20% U(7,30) |
| `training_dataset` | 2 | 14 | high | 70% U(7,30) + 30% U(30,60) |

Nguồn của h_i, delay và min TTL của raw, curated: bảng giả định trong `docs/lakehouse-summary-topic-5.md`, mục II.7. Giá trị min TTL của `training_dataset` (14 ngày) là **quyết định mới của contract**: tài liệu nguồn chỉ nói yêu cầu tái lập được đánh giá riêng. Người kiểm tra xác nhận hoặc đổi trước khi mở holdout.

TTL grid dùng chung: `[1, 7, 14, 30, 60, 90]`. Không gian tìm kiếm 6^3 = 216 vector, trong đó 66 vector khả thi ở B = 810 sau khi loại vi phạm min TTL và budget.

## 4. Tuổi phiên bản, boundary và incident mất hạ tầng

Ký hiệu cho một sự cố:

- `A = t_bad - t_target`: khoảng cách từ phiên bản sạch đến commit lỗi.
- `D = t_detect - t_bad`: độ trễ phát hiện.
- `L = t_restore - t_detect`: độ trễ phản ứng sau phát hiện.

**Tuổi phiên bản cần phục hồi: `H = A + D + L`.**

Quy tắc phục hồi cho mô phỏng TTL lý tưởng:

```
recoverable(e, ttl) = (not e.infrastructure_lost) and (e.target_age_days <= ttl[e.table_id])
```

- **Boundary `H = TTL` là phục hồi được** (bao gồm). `H > TTL` là mất. Fixture kiểm tra dùng số nguyên hoặc số nhị phân chính xác để tránh sai số float.
- Cấu hình chính (S0): `A = 0`, `L = 0`, nên `H = D`. Giả định này được ghi rõ trong report. S3 nới `L` để kiểm tra độ nhạy.
- **Incident mất hạ tầng**: mất cả dữ liệu hiện tại và lịch sử trong cùng failure domain, không có bản sao độc lập. Luôn `recoverable = false` với mọi policy. Trần coverage lý tưởng của S1 là 92%, nên mục tiêu coverage 95% không khả thi ở S1.
- Cùng một danh sách incident được đánh giá bởi cả hai policy (so sánh theo cặp).

## 5. Scenario (đóng băng trước khi mở holdout)

| ID | Mô tả | Thay đổi so với S0 | Dùng ở split |
| --- | --- | --- | --- |
| `S0_main` | Mô hình lý tưởng, không mất hạ tầng | không | development, holdout |
| `S1_infra_loss` | 8% incident mất hạ tầng (24/300 mỗi profile, đếm cố định, vị trí theo seed) | `infra_loss_rate = 0.08` | development, holdout |
| `S2_tail_shift` | Đuôi delay của raw dài hơn | raw: 80% U(0,2) + 20% U(2,25) | shift |
| `S3_slow_response` | Phản ứng chậm sau phát hiện | `L ~ U(0,3)` | shift |

Scenario shift chỉ chạy qua evaluator trên policy đã khóa. Không chỉnh policy hay scenario sau khi thấy kết quả.

## 6. Development và holdout

| Split | Scenario | Seed | Optimizer được đọc |
| --- | --- | --- | --- |
| `development` | S0, S1 | 1001 đến 1010 | có |
| `holdout` | S0, S1 | 2001 đến 2010 | không |
| `shift` | S2, S3 | 3001 đến 3010 | không |

- Mỗi (split, scenario, seed) có 300 incident mỗi profile, tổng 900 (yêu cầu của đề: ít nhất 100).
- RNG: `numpy.random.default_rng(SeedSequence([seed, scenario_index, profile_index]))`, một generator độc lập cho mỗi (seed, scenario, profile). Cùng config và seed cho cùng dữ liệu.
- API optimizer chỉ nhận `dev_events`. Holdout và shift chỉ đi vào evaluator.
- Khóa policy (TASK-12) ghi `config_hash` và `locked_on_split = "development"` trước khi chạy holdout. Đổi profile, grid, scenario hoặc budget sau thời điểm khóa làm kết quả holdout không hợp lệ và phải sinh lại từ đầu.

## 7. Baseline, optimizer, tie-break

- **Baseline (TTL chung):** TTL lớn nhất trong grid thỏa `ttl >= max(min_ttl)` và `sum(h_i) * ttl <= B`. Ở B = 810 với `sum(h_i) = 27`, baseline = 30 ngày, cost = 810 GB (dùng hết budget).
- **Optimizer:** duyệt toàn bộ 216 vector, loại vi phạm min TTL hoặc budget, chọn coverage cao nhất trên development.
- **Tie-break:** cost thấp hơn, rồi thứ tự từ điển của vector TTL theo thứ tự profile (`raw_ingest`, `curated_business`, `training_dataset`).
- Không có vector khả thi: trả về trạng thái `infeasible`, không âm thầm bỏ ràng buộc. Ví dụ B = 300 làm baseline infeasible (cần TTL >= 14 nên cost >= 378), vì vậy sweep dùng `[450, 600, 810, 1200, 1620]`.
- Kết luận chỉ đúng trên grid và mô hình đã chọn, không khẳng định tối ưu cho TTL liên tục hay engine thật.

**Rủi ro biết trước:** quy tắc tie-break theo cost thấp nhất khiến optimizer chọn TTL khít với đuôi delay của development (ở S0 là vector khoảng `(7, 30, 60)` với cost 410 GB). Vector khít này có thể mất coverage ở S2 và S3 vì không còn dư địa cho đuôi delay mới. Đây là giả thuyết thất bại chưa được kiểm chứng; chỉ ghi là quan sát sau khi chạy eval thật.

## 8. Metric chính và metric phụ

**Chính: Recovery Coverage tại fixed budget (B = 810 GB).**

```
RecoveryCoverage = recoverable_incidents / total_incidents
delta_pp = 100 * (coverage_ours - coverage_baseline)    # điểm phần trăm
```

Mẫu số gồm cả incident mất hạ tầng (S1). Báo cáo thêm bản chỉ lỗi logic để thấy riêng giới hạn của retention.

Metric phụ: coverage theo profile; logical-only coverage; infra-loss coverage; cost thực (GB) và phần budget dư; số vi phạm budget; số vi phạm min TTL; storage multiplier khi mô hình hóa được. Không báo cáo RPO/RTO vì chưa mô hình hóa điểm phục hồi.

Đường Pareto: quét B trong sweep, mỗi B khóa policy từ development rồi đánh giá holdout. B chính là 810, không chọn lại B sau khi thấy kết quả.

Kiểm tra giá trị tay (S0, ideal, kỳ vọng phân tích): TTL chung 30 cho coverage 0.90 (raw 1.0, curated 1.0, training 0.7); vector `(14, 60, 90)` cho 1.0. Các con số này là tính toán lý thuyết, không phải kết quả đo.

## 9. Schema dùng chung

### 9.1. Config

Cấu trúc theo `configs/experiment.sample.json`: `meta`, `units`, `budget`, `ttl_grid_days`, `profiles[]`, `version_age`, `scenarios[]`, `splits`, `incidents_per_profile`, `rng`, `optimizer`, `baseline`, `run_id_format`, `config_hash`.

**Config hash:** sha256 của JSON chuẩn tắc (`sort_keys=true`, `separators=(",",":")`) sau khi bỏ `meta.status` và `meta.note`; lấy 8 ký tự đầu.

### 9.2. Incident (JSONL, một dòng một incident)

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `incident_id` | string | `{split}-{scenario}-s{seed}-{table_id}-{index:04d}` |
| `split` | enum | `development`, `holdout`, `shift` |
| `scenario` | string | ID scenario |
| `seed` | int | seed của lần sinh |
| `table_id` | string | thuộc profile đã khai báo |
| `anchor_gap_days` | float | A |
| `detect_delay_days` | float | D |
| `response_lag_days` | float | L |
| `target_age_days` | float | H, bắt buộc bằng A + D + L (validator kiểm tra) |
| `infrastructure_lost` | bool | mất hạ tầng, không backup độc lập |

### 9.3. Policy (JSON)

| Trường | Ý nghĩa |
| --- | --- |
| `policy_id` | ví dụ `baseline_uniform`, `optimized_per_profile` |
| `kind` | `baseline_uniform` hoặc `optimized_per_profile` |
| `ttl_days` | ánh xạ `table_id` sang số ngày |
| `budget_gb`, `cost_gb` | budget và cost thực |
| `feasible` | bool; false thì không đánh giá thành kết quả hợp lệ |
| `config_hash` | hash khi khóa |
| `locked_on_split` | luôn `development` |
| `locked_at` | ISO 8601 với offset +07:00 |

### 9.4. Metrics (JSON, một file cho một lần eval)

| Trường | Ý nghĩa |
| --- | --- |
| `run_id`, `config_hash`, `status` | `status` là `valid`, `invalid` hoặc `error` |
| `split`, `scenario`, `seed` | khóa của từng bản ghi |
| `policies.{policy_id}` | `coverage_total`, `coverage_by_profile`, `recoverable`, `total`, `coverage_logical_only`, `coverage_infra_loss`, `cost_gb`, `budget_violations`, `min_ttl_violations` |
| `paired.delta_pp` | chênh lệch theo cặp, mỗi seed một giá trị |
| `aggregate` | trung bình, độ lệch chuẩn qua 10 seed |
| `failure_cases` | danh sách mô tả failure đã quan sát |

Run vượt budget hoặc input sai schema được ghi `invalid` kèm lý do, không trình bày như cải thiện hợp lệ.

### 9.5. Run ID

`{YYYYMMDD}T{HHMMSS}-{split}-{config_hash8}`, giờ UTC+7. Một lần gọi lệnh eval có một run ID duy nhất, liên kết config, policy, metrics, report HTML và nhận xét LLM. Không ghi đè run cũ. Báo cáo lưu tại `reports/<run_id>/`.

## 10. Fixture cho TASK-07 và TASK-04 (đáp án tính tay)

| # | Tình huống | Đầu vào | Kết quả mong đợi |
| --- | --- | --- | --- |
| F1 | H < TTL | raw, H = 0.5, TTL = 1 | recoverable |
| F2 | H = TTL | raw, H = 1.0, TTL = 1 | recoverable |
| F3 | H > TTL | raw, H = 1.5, TTL = 1 | không recoverable |
| F4 | mất hạ tầng | H = 0.1, TTL = 90, `infrastructure_lost = true` | không recoverable |
| F5 | TTL chung | `(30,30,30)` | cost 810, hợp lệ ở B = 810 |
| F6 | TTL riêng | `(14,60,90)` | cost 760, hợp lệ ở B = 810 |
| F7 | vượt budget | `(90,90,90)` | cost 2430, `budget_violation` |
| F8 | vi phạm min TTL | `(1,7,7)` | `min_ttl_violation` (training < 14) |
| F9 | budget thấp hơn minimum | B = 300, TTL chung | baseline `infeasible` |
| F10 | vector tối thiểu | `(1,7,14)` | cost 83 |

## 11. Việc còn mở cần người kiểm tra xác nhận

1. Min TTL của `training_dataset` = 14 ngày (quyết định mới, mục 3).
2. B chính = 810 GB, chọn bằng đúng cost của TTL chung 30 ngày để baseline dùng hết budget và so sánh công bằng.
3. Tham số S2 (đuôi raw tới 25 ngày) và S3 (`L` tới 3 ngày) là giả định, đóng băng khi khóa contract.
4. 300 incident mỗi profile và 10 seed mỗi split là đề xuất; có thể tăng nếu còn thời gian, không giảm dưới 100 incident tổng.

## 12. Nguồn

- `docs/lakehouse-summary-topic-5.md`: giả định profile, mô hình H = A + D + L, protocol thí nghiệm.
- `docs/issue-plan.md`: TASK-01, các phụ thuộc và quy tắc phối hợp.
- Delta Lake data retention và table utility commands; Apache Iceberg maintenance. Ngày đối chiếu ghi trong `docs/research-notes.md` (TASK-03).
