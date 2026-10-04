# Kế hoạch issue: Retention Policy Optimizer

Repo: [rin1652/Retention-Policy-Optimizer-Data-Lakehouse](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse)  
Ngày lập: 04/10/2026. Múi giờ: **Asia/Ho_Chi_Minh (UTC+7), giờ Việt Nam**.

## Contract dùng chung đã chốt

Issue #1 đã được hoàn thiện kỹ thuật theo yêu cầu người dùng. Các issue triển khai dùng [contract v1.0](experiment-contract.md) và [config chuẩn](../configs/experiment.sample.json): budget chính 810 GB, table_id `raw_ingest`/`curated_business`/`training_dataset`, field `infrastructure_lost`, routing seed/scenario và run ID có UUID. Các phác thảo schema trước trong kế hoạch này phải được đối chiếu contract; khi khác nhau, contract v1.0 là nguồn dùng cho code. Xem [biên bản kiểm tra](issue-01-review.md).

## Lịch và phạm vi

**Lịch đề xuất: 09:00–11:00 ngày 05/10/2026.** T0 = 09:00, deadline bộ nộp = 11:00. Đây là lịch tạm theo sprint 2 giờ trong PDF vì nhóm chưa xác nhận thời gian bắt đầu/nộp; không phải hạn nộp do giảng viên công bố. Các issue đều ghi rõ trạng thái đề xuất. Khi đổi T0, dịch đồng bộ toàn bộ mốc theo chênh lệch thời gian.

Mục tiêu: mô phỏng Python, tối đa RecoveryCoverage ở cùng history-overhead budget, so sánh TTL chung với TTL từng profile; mỗi lần eval xuất report HTML có 3–5 câu nhận xét LLM dựa trên kết quả thật. Đầu ra là mô phỏng có thể chạy lại, không chỉ tài liệu/slide.

Đây là kế hoạch công việc; các tiêu chí dưới đây chưa được đánh dấu hoàn thành. Không yêu cầu triển khai toàn bộ code trong bước lập issue.

## Phân công

| Thành viên | Trách nhiệm | Issue |
|---|---|---|
| Nguyễn Đình Phúc | Mô hình, nghiên cứu, prompt/client LLM, README và pitch | TASK-01, 03, 09, 14 |
| Đoàn Tuấn Long | Môi trường, generator, scenario, kiểm tra tái lập | TASK-02, 05, 11, 15 |
| Nguyễn Việt Thành | Cost model, baseline, optimizer, khóa policy | TASK-04, 06, 08, 12 |
| Đinh Ngọc Đức | Evaluator, report HTML, eval chính, đóng gói | TASK-07, 10, 13, 16 |

Để giảm phần việc dồn vào Đức, Phúc phụ trách cả client LLM và prompt; Đức tích hợp đầu ra vào HTML. Phân công này cụ thể hóa và điều chỉnh kế hoạch trước. GitHub username: Phúc `rin1652`, Long `tlong1610`, Thành `thanhnvhust514`, Đức `dinhngocduc1311`. Nếu GitHub chưa cho phép gán một tài khoản, giữ người phụ trách theo họ tên trong body và ghi rõ trạng thái chưa gán.

## Bảng issue và deadline

Tất cả giờ dưới đây thuộc **05/10/2026, UTC+7**. P0 là công việc cần cho bộ nộp.

| ID | Công việc | Người phụ trách | Bắt đầu | Deadline | Phụ thuộc |
|---|---|---|---|---|---|
| TASK-01 | Chốt giả thuyết, budget và schema dùng chung | Nguyễn Đình Phúc | 09:00 | **09:10** | — |
| TASK-02 | Khởi tạo môi trường và mẫu dữ liệu tích hợp | Đoàn Tuấn Long | 09:00 | **09:20** | — |
| TASK-03 | Đối chiếu retention docs và chuẩn bị cấu hình LLM | Nguyễn Đình Phúc | 09:10 | **09:30** | TASK-01 |
| TASK-04 | Xây cost model và kiểm tra budget | Nguyễn Việt Thành | 09:10 | **09:30** | TASK-01 |
| TASK-05 | Sinh development và holdout tái lập được | Đoàn Tuấn Long | 09:20 | **09:45** | TASK-01, TASK-02 |
| TASK-06 | Xây baseline TTL chung công bằng | Nguyễn Việt Thành | 09:30 | **09:45** | TASK-01, TASK-04 |
| TASK-07 | Xây evaluator độc lập và kiểm tra correctness | Đinh Ngọc Đức | 09:10 | **09:40** | TASK-01 |
| TASK-08 | Tối ưu TTL theo profile bằng grid search | Nguyễn Việt Thành | 09:45 | **10:10** | TASK-04, TASK-05, TASK-06 |
| TASK-09 | Tích hợp nhận xét LLM dựa trên kết quả eval | Nguyễn Đình Phúc | 09:30 | **10:10** | TASK-01, TASK-03 |
| TASK-10 | Sinh report HTML cho từng lần eval | Đinh Ngọc Đức | 09:40 | **10:10** | TASK-01, TASK-07 |
| TASK-11 | Chuẩn bị failure case và holdout dịch chuyển phân phối | Đoàn Tuấn Long | 09:45 | **10:10** | TASK-01, TASK-05 |
| TASK-12 | Khóa policy và kiểm tra tích hợp trước holdout | Nguyễn Việt Thành | 10:10 | **10:20** | TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11 |
| TASK-13 | Chạy eval chính, nhiều seed và xuất evidence | Đinh Ngọc Đức | 10:20 | **10:40** | TASK-12 |
| TASK-14 | Hoàn thiện README và nội dung pitch 4 slide | Nguyễn Đình Phúc | 10:10 | **10:50** | TASK-03, TASK-09, TASK-12, TASK-13 |
| TASK-15 | Kiểm tra tái lập và đối chiếu report lần cuối | Đoàn Tuấn Long | 10:40 | **10:55** | TASK-13 |
| TASK-16 | Tổng hợp bàn giao và bộ nộp cuối | Đinh Ngọc Đức | 10:40 | **11:00** | TASK-13, TASK-14, TASK-15 |

## Liên kết GitHub issue

- [TASK-01 / #1](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1) — Chốt giả thuyết, budget và schema dùng chung
- [TASK-02 / #2](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/2) — Khởi tạo môi trường và mẫu dữ liệu tích hợp
- [TASK-03 / #3](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/3) — Đối chiếu retention docs và chuẩn bị cấu hình LLM
- [TASK-04 / #4](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/4) — Xây cost model và kiểm tra budget
- [TASK-05 / #5](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/5) — Sinh development và holdout tái lập được
- [TASK-06 / #6](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/6) — Xây baseline TTL chung công bằng
- [TASK-07 / #7](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/7) — Xây evaluator độc lập và kiểm tra correctness
- [TASK-08 / #8](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/8) — Tối ưu TTL theo profile bằng grid search
- [TASK-09 / #9](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/9) — Tích hợp nhận xét LLM dựa trên kết quả eval
- [TASK-10 / #10](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/10) — Sinh report HTML cho từng lần eval
- [TASK-11 / #11](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/11) — Chuẩn bị failure case và holdout dịch chuyển phân phối
- [TASK-12 / #12](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/12) — Khóa policy và kiểm tra tích hợp trước holdout
- [TASK-13 / #13](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/13) — Chạy eval chính, nhiều seed và xuất evidence
- [TASK-14 / #14](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/14) — Hoàn thiện README và nội dung pitch 4 slide
- [TASK-15 / #15](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/15) — Kiểm tra tái lập và đối chiếu report lần cuối
- [TASK-16 / #16](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/16) — Tổng hợp bàn giao và bộ nộp cuối

## Các mốc bàn giao

| Deadline | Kết quả phải có |
|---|---|
| 09:10 | Contract/schema và metric đã chốt |
| 09:30 | Cost model, tài liệu nền và cấu hình LLM sẵn sàng |
| 09:45 | Generator, baseline và evaluator hoạt động |
| 10:10 | Optimizer, LLM client, report HTML và failure scenario sẵn sàng |
| 10:20 | Policy/config khóa trước holdout; pipeline ghép được |
| 10:40 | Eval chính hoàn tất, evidence và report thật có LLM |
| 10:50 | README và pitch hoàn thiện |
| 10:55 | Kiểm tra tái lập/report hoàn tất |
| 11:00 | Bộ nộp được kiểm tra và bàn giao |

Issue có thể bắt đầu chuẩn bị trước khi dependency xong; phần nghiệm thu và bàn giao chỉ hoàn thành khi dependency cần thiết đã sẵn sàng. Ví dụ README được viết nháp từ 10:10 và chỉ điền kết quả sau 10:40; đóng gói được chuẩn bị song song với QA.

## Chi tiết issue

### TASK-01 — Chốt giả thuyết, budget và schema dùng chung

**Người phụ trách:** Nguyễn Đình Phúc
**GitHub assignee:** `rin1652` — đã gán.
**Người kiểm tra:** Nguyễn Việt Thành
**Bắt đầu đề xuất:** 05/10/2026 09:00 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:10 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Ghi giả thuyết: TTL riêng cải thiện RecoveryCoverage ở cùng history-overhead budget.
- [ ] Chốt 3 profile, đơn vị GB/ngày, minimum TTL, grid TTL và các scenario trước khi mở holdout.
- [ ] Định nghĩa tuổi phiên bản H=A+D+L, boundary H=TTL và incident mất hạ tầng.
- [ ] Chốt schema config, incident, policy và metrics; quy ước development/holdout, run ID.

## Đầu ra

docs/experiment-contract.md; config mẫu

## Phụ thuộc

Không có; bắt đầu theo lịch. Nếu cần schema, dùng draft rồi đối chiếu TASK-01.

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-02 — Khởi tạo môi trường và mẫu dữ liệu tích hợp

**Người phụ trách:** Đoàn Tuấn Long
**GitHub assignee:** `tlong1610` — chưa gán được vì tài khoản chưa đủ điều kiện assignee trong repo. Chủ repo cần thêm/hoàn tất quyền cộng tác viên, sau đó gán 4 issue của Long.
**Người kiểm tra:** Đinh Ngọc Đức
**Bắt đầu đề xuất:** 05/10/2026 09:00 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:20 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Tạo cấu trúc src/, configs/, tests/, reports/ và khai báo dependencies/version Python.
- [ ] Chuẩn bị .gitignore phù hợp; API key không đưa vào repo.
- [ ] Sau khi TASK-01 chốt schema, tạo mẫu incident nhỏ có expected outcome rõ ràng.
- [ ] Ghi lệnh setup và thống nhất giao diện import để các module ghép được.

## Đầu ra

requirements.txt hoặc pyproject.toml; sample fixture; hướng dẫn setup

## Phụ thuộc

Không có; bắt đầu theo lịch. Nếu cần schema, dùng draft rồi đối chiếu TASK-01.

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-03 — Đối chiếu retention docs và chuẩn bị cấu hình LLM

**Người phụ trách:** Nguyễn Đình Phúc
**GitHub assignee:** `rin1652` — đã gán.
**Người kiểm tra:** Đinh Ngọc Đức
**Bắt đầu đề xuất:** 05/10/2026 09:10 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:30 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Ghi nguồn Delta/Iceberg cùng ngày truy cập; phân biệt time travel, rollback và backup.
- [ ] Ghi giới hạn cost tuyến tính và TTL simulator; không coi TTL mô phỏng là cấu hình VACUUM production.
- [ ] Chọn provider/model, cách cấu hình credential trong môi trường và xác nhận có thể gọi LLM.
- [ ] Soạn prompt 3–5 câu dựa trên metrics; xác định timeout và cách ghi lỗi.

## Đầu ra

docs/research-notes.md; prompts/report-commentary.txt; .env.example không chứa key

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-04 — Xây cost model và kiểm tra budget

**Người phụ trách:** Nguyễn Việt Thành
**GitHub assignee:** `thanhnvhust514` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 09:10 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:30 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Tính history cost = tổng history_gb_per_day * retention_days, thống nhất với budget GB.
- [ ] Kiểm tra minimum TTL, số âm, profile thiếu và policy không khả thi.
- [ ] Phân biệt history overhead với current-data size; không dùng ingest rate thay cost nếu chưa giả định rõ.
- [ ] Có kiểm tra tính toán tay và trường hợp budget không đáp ứng minimum retention.

## Đầu ra

src/cost_model.py; kiểm tra budget/cost

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-05 — Sinh development và holdout tái lập được

**Người phụ trách:** Đoàn Tuấn Long
**GitHub assignee:** `tlong1610` — chưa gán được vì tài khoản chưa đủ điều kiện assignee trong repo. Chủ repo cần thêm/hoàn tất quyền cộng tác viên, sau đó gán 4 issue của Long.
**Người kiểm tra:** Nguyễn Việt Thành
**Bắt đầu đề xuất:** 05/10/2026 09:20 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:45 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Sinh raw/curated/training với detection-delay distribution ghi trong config.
- [ ] Có seed riêng development/holdout; ít nhất 100 incident trong mỗi tập, đề xuất 1.000 nếu đủ thời gian.
- [ ] Incident chứa table_id, scenario, target_age_days, infrastructure_lost và các thông tin cần tái lập.
- [ ] Cùng seed/config tạo cùng dữ liệu; xuất thống kê số incident và delay theo profile.

## Đầu ra

src/generator.py; configs/profiles.json; dữ liệu development/holdout

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)
- [TASK-02](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/2)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-06 — Xây baseline TTL chung công bằng

**Người phụ trách:** Nguyễn Việt Thành
**GitHub assignee:** `thanhnvhust514` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 09:30 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:45 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Chọn TTL chung lớn nhất trong grid thỏa budget và mọi minimum retention.
- [ ] Không dùng một TTL vượt budget hoặc tùy ý quá thấp làm baseline chính.
- [ ] Xuất vector TTL, actual cost và trạng thái feasibility.
- [ ] Có case tính tay; baseline chỉ dùng thông tin được phép, không xem kết quả holdout.

## Đầu ra

src/policies.py: baseline; baseline policy JSON

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)
- [TASK-04](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/4)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-07 — Xây evaluator độc lập và kiểm tra correctness

**Người phụ trách:** Đinh Ngọc Đức
**GitHub assignee:** `dinhngocduc1311` — đã gán.
**Người kiểm tra:** Đoàn Tuấn Long
**Bắt đầu đề xuất:** 05/10/2026 09:10 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 09:40 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Tính recoverable khi không mất hạ tầng và target_age_days <= TTL; ghi đây là mô hình lý tưởng.
- [ ] Tính coverage tổng/theo profile, số recoverable/total, cost và violations theo schema.
- [ ] Run vượt budget hoặc input sai được ghi invalid; không trình bày như một cải thiện hợp lệ.
- [ ] Dùng fixture nhỏ kiểm tra H<TTL, H=TTL, H>TTL, mất hạ tầng và budget violation.

## Đầu ra

src/evaluate.py; tests/ hoặc fixture có ground truth

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-08 — Tối ưu TTL theo profile bằng grid search

**Người phụ trách:** Nguyễn Việt Thành
**GitHub assignee:** `thanhnvhust514` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 09:45 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:10 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Duyệt vector TTL khả thi, tối đa coverage trên development.
- [ ] Không nhận holdout trong API optimizer; quy tắc tie-break ưu tiên cost thấp rồi thứ tự ổn định.
- [ ] Xuất TTL tối ưu, cost, dev score và config; không khẳng định tối ưu ngoài grid.
- [ ] So sánh với nghiệm tính tay trên bài toán nhỏ và xử lý không có policy khả thi.

## Đầu ra

src/policies.py: optimizer; optimized policy JSON

## Phụ thuộc

- [TASK-04](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/4)
- [TASK-05](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/5)
- [TASK-06](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/6)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-09 — Tích hợp nhận xét LLM dựa trên kết quả eval

**Người phụ trách:** Nguyễn Đình Phúc
**GitHub assignee:** `rin1652` — đã gán.
**Người kiểm tra:** Đinh Ngọc Đức
**Bắt đầu đề xuất:** 05/10/2026 09:30 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:10 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Xây hàm nhận metrics JSON và tạo 3–5 câu nhận xét tiếng Việt qua một lời gọi LLM thật.
- [ ] LLM chỉ diễn giải số đo; không tính lại metric, thay TTL hoặc điều khiển optimizer.
- [ ] Lưu model, prompt, response, status và run ID; dùng key từ môi trường.
- [ ] Nếu LLM timeout/lỗi, trả trạng thái thiếu nhận xét để HTML vẫn xuất; không thay bằng đoạn giả.

## Đầu ra

src/llm_commentary.py; prompt; cấu hình provider/model

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)
- [TASK-03](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/3)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-10 — Sinh report HTML cho từng lần eval

**Người phụ trách:** Đinh Ngọc Đức
**GitHub assignee:** `dinhngocduc1311` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 09:40 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:10 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Render metrics JSON thành report HTML có run ID, thời gian UTC+7, config, TTL, budget và trạng thái.
- [ ] Có bảng baseline/phương pháp, coverage theo profile, cost, chênh lệch điểm phần trăm và biểu đồ nhúng.
- [ ] Có vùng nhận xét LLM, trạng thái lỗi và failure case; khi TASK-09 xong nối phản hồi vào template.
- [ ] Lưu reports/<run_id>/report.html và dữ liệu JSON/CSV, không ghi đè run cũ; mở offline đọc được.

## Đầu ra

src/report.py; template HTML; report thử có nhãn dữ liệu fixture

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)
- [TASK-07](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/7)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-11 — Chuẩn bị failure case và holdout dịch chuyển phân phối

**Người phụ trách:** Đoàn Tuấn Long
**GitHub assignee:** `tlong1610` — chưa gán được vì tài khoản chưa đủ điều kiện assignee trong repo. Chủ repo cần thêm/hoàn tất quyền cộng tác viên, sau đó gán 4 issue của Long.
**Người kiểm tra:** Đinh Ngọc Đức
**Bắt đầu đề xuất:** 05/10/2026 09:45 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:10 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Tạo kịch bản mất hạ tầng không có backup độc lập và kịch bản tail delay dài hơn.
- [ ] Giữ scenario config đã chốt; không chỉnh theo kết quả optimizer/holdout.
- [ ] Lưu cùng incident để hai policy được đánh giá theo cặp; ghi số incident từng loại.
- [ ] Mô tả failure dự kiến của mô hình; kết luận quan sát chỉ bổ sung sau eval thực.

## Đầu ra

configs/scenarios.json; dữ liệu failure/shift; mô tả scenario

## Phụ thuộc

- [TASK-01](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1)
- [TASK-05](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/5)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-12 — Khóa policy và kiểm tra tích hợp trước holdout

**Người phụ trách:** Nguyễn Việt Thành
**GitHub assignee:** `thanhnvhust514` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 10:10 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:20 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Ghép generator, cost, policies, evaluator, LLM và report bằng development/fixture.
- [ ] Xuất policy baseline/optimized đã khóa cùng config ID hoặc hash trước đánh giá holdout.
- [ ] Rà cost <= cùng budget, mọi minimum TTL và interface giữa các module.
- [ ] Nếu lỗi, sửa bằng development/fixture; không tune theo kết quả holdout.

## Đầu ra

policy/config đã khóa; ghi nhận preflight; nội dung slide 2

## Phụ thuộc

- [TASK-05](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/5)
- [TASK-06](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/6)
- [TASK-07](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/7)
- [TASK-08](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/8)
- [TASK-09](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/9)
- [TASK-10](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/10)
- [TASK-11](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/11)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-13 — Chạy eval chính, nhiều seed và xuất evidence

**Người phụ trách:** Đinh Ngọc Đức
**GitHub assignee:** `dinhngocduc1311` — đã gán.
**Người kiểm tra:** Đoàn Tuấn Long
**Bắt đầu đề xuất:** 05/10/2026 10:20 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:40 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Cung cấp một lệnh eval chạy baseline và phương pháp trên cùng holdout/scenario.
- [ ] Đề xuất 10 seed, báo trung bình/độ lệch chuẩn hoặc chênh lệch theo cặp; khóa seed/config trước test.
- [ ] Xuất report HTML và nhận xét LLM cho mỗi lần gọi eval; chạy failure/shift và sweep budget đã định để có Pareto.
- [ ] Lưu metrics JSON/CSV, policy, config, lệnh chạy và kết luận thực; không bịa hoặc chọn lọc run có lợi.

## Đầu ra

lệnh eval; reports thật; results.csv; biểu đồ; nội dung slide 3–4

## Phụ thuộc

- [TASK-12](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/12)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-14 — Hoàn thiện README và nội dung pitch 4 slide

**Người phụ trách:** Nguyễn Đình Phúc
**GitHub assignee:** `rin1652` — đã gán.
**Người kiểm tra:** Đinh Ngọc Đức
**Bắt đầu đề xuất:** 05/10/2026 10:10 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:50 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Viết nháp từ 10:10; điền số liệu sau TASK-13, đối chiếu đúng run ID.
- [ ] README có vấn đề, giả thuyết, setup, lệnh eval, metric, kết quả và failure case.
- [ ] Hướng dẫn cấu hình LLM và vị trí HTML/JSON/CSV; ghi xử lý lỗi và các giới hạn.
- [ ] Tổng hợp nội dung 4 slide Pain/Method/Evidence/Decision từ phần của các thành viên.

## Đầu ra

README.md; docs/pitch-outline.md; source notes

## Phụ thuộc

- [TASK-03](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/3)
- [TASK-09](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/9)
- [TASK-12](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/12)
- [TASK-13](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/13)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-15 — Kiểm tra tái lập và đối chiếu report lần cuối

**Người phụ trách:** Đoàn Tuấn Long
**GitHub assignee:** `tlong1610` — chưa gán được vì tài khoản chưa đủ điều kiện assignee trong repo. Chủ repo cần thêm/hoàn tất quyền cộng tác viên, sau đó gán 4 issue của Long.
**Người kiểm tra:** Nguyễn Việt Thành
**Bắt đầu đề xuất:** 05/10/2026 10:40 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 10:55 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Chạy lại bằng lệnh tài liệu trên môi trường sạch hoặc venv mới; không cần biết setup ngầm.
- [ ] Đối chiếu số liệu HTML với JSON/CSV, run ID và policy; phần nhận xét LLM không sai số đo.
- [ ] Chạy hai lần eval, xác nhận có hai report riêng và mỗi report có nhận xét LLM thật.
- [ ] Mở report kiểm tra bảng/biểu đồ/tiếng Việt, failure status và đường dẫn dữ liệu; ghi pass/fail.

## Đầu ra

docs/verification.md; bằng chứng chạy lại và QA report

## Phụ thuộc

- [TASK-13](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/13)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)

### TASK-16 — Tổng hợp bàn giao và bộ nộp cuối

**Người phụ trách:** Đinh Ngọc Đức
**GitHub assignee:** `dinhngocduc1311` — đã gán.
**Người kiểm tra:** Nguyễn Đình Phúc
**Bắt đầu đề xuất:** 05/10/2026 10:40 (Asia/Ho_Chi_Minh, UTC+7)
**Deadline đề xuất:** 05/10/2026 11:00 (UTC+7)
**Ưu tiên:** P0 — cần cho bộ nộp

> Lịch tạm theo sprint 2 giờ 09:00–11:00; nhóm chưa xác nhận giờ bắt đầu/nộp. Đây không phải deadline do giảng viên công bố. Nếu đổi T0, dịch đồng bộ các mốc và giữ nguyên thứ tự phụ thuộc.

## Công việc và tiêu chí hoàn thành

- [ ] Chuẩn bị từ 10:40; chỉ chốt sau README và kiểm tra tái lập hoàn tất.
- [ ] Bộ nộp gồm code/config/version, README, evidence thực, HTML có LLM và pitch tối đa 4 slide.
- [ ] Kiểm tra đủ 3 profile, >=100 incident, cùng budget, baseline, holdout và failure case.
- [ ] Cập nhật link artifacts vào issue, ghi vấn đề còn mở và commit cuối; không đổi metric hoặc tune sau holdout.

## Đầu ra

bộ nộp; checklist cuối; commit/PR và link report

## Phụ thuộc

- [TASK-13](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/13)
- [TASK-14](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/14)
- [TASK-15](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/15)

## Bàn giao

- [ ] Đưa commit/PR và đường dẫn đầu ra vào issue.
- [ ] Người kiểm tra xác nhận tiêu chí hoàn thành trước khi đóng.
- [ ] Nếu bị chặn hoặc trễ, cập nhật nguyên nhân, việc còn thiếu và giờ dự kiến mới.

[Tài liệu kế hoạch](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/issue-plan.md) · [Tóm tắt và phân tích đề tài](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/blob/main/docs/lakehouse-summary-topic-5.md)


## Quy tắc phối hợp

- Một issue có một người chịu trách nhiệm chính và một người kiểm tra; các thành viên khác có thể hỗ trợ.
- Ghi trạng thái trong issue: Todo, In progress, Blocked hoặc Done. Khi bị chặn, nêu dependency và cập nhật giờ dự kiến, không âm thầm bỏ việc.
- Dùng branch theo issue và PR có link issue khi phát triển code; thời điểm đóng issue là sau khi review và có đầu ra kiểm chứng được.
- Optimizer chỉ dùng development; khóa policy trước holdout. LLM chỉ diễn giải metric do evaluator tính.
- Một run ID liên kết config, policy, metrics, report và nhận xét LLM. Giữ report của từng lần chạy.
- Nếu call LLM lỗi, vẫn xuất HTML ghi thiếu nhận xét. Issue LLM/report chưa đạt yêu cầu nghiệm thu cho đến khi có lời gọi thật thành công.
- Nếu có nguy cơ trễ 11:00, ưu tiên thí nghiệm hợp lệ, baseline, HTML+LLM và tái lập; đơn giản hóa trình bày/biểu đồ. Không bỏ correctness hoặc tạo số liệu giả.

## Checklist bộ nộp

- [ ] Ba table profile và phân phối delay được ghi rõ.
- [ ] Ít nhất 100 incident trong tập đánh giá; development/holdout riêng.
- [ ] Baseline và phương pháp cùng budget, cùng dữ liệu, cùng cost model.
- [ ] Policy/config khóa trước holdout; kiểm tra budget và correctness.
- [ ] Có mất hạ tầng và ít nhất một failure/edge case được phân tích.
- [ ] Kết quả từ chạy thật, có bảng/biểu đồ và thông tin seed/version.
- [ ] Mỗi lần eval sinh report HTML riêng; có nhận xét LLM thật và lưu trace.
- [ ] README có lệnh tái lập và cấu hình LLM; report khớp JSON/CSV.
- [ ] Pitch tối đa 4 slide và bộ nộp có liên kết artifacts.

## Nguồn yêu cầu

Tóm tắt PDF và phân tích đề tài trong [lakehouse-summary-topic-5.md](lakehouse-summary-topic-5.md). Yêu cầu HTML mỗi eval và nhận xét LLM do người dùng bổ sung từ hướng dẫn của giảng viên. Mốc giờ và cấu trúc issue là đề xuất kế hoạch; chưa được giảng viên/nhóm xác nhận.


