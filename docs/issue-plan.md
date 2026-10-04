# Kế hoạch issue MVP: Retention Policy Optimizer

Cập nhật **04/10/2026** theo yêu cầu người dùng làm nhanh và đơn giản hơn. Repo: [rin1652/Retention-Policy-Optimizer-Data-Lakehouse](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse).

[Phạm vi MVP](mvp-scope.md) là tiêu chí triển khai hiện tại. Giữ [contract v1.0](experiment-contract.md) cho profile/schema/cost/RNG; MVP chỉ chạy S0 dev1001/holdout2001 ở 810 GB, thêm một failure case S1 khi đo. Không yêu cầu chạy hết 10 seed, S2/S3 hoặc sweep. Mỗi eval vẫn phải có HTML và nhận xét LLM thật.

## Lịch và phân công

Tất cả giờ trong bảng thuộc **05/10/2026, UTC+7**, lịch đề xuất 09:00–11:00 chưa được nhóm xác nhận; không phải deadline do giảng viên công bố.

| Issue | Việc | Phụ trách | Bắt đầu | Deadline | Phụ thuộc | Trạng thái khi cập nhật |
|---|---|---|---|---|---|---|
| [#1](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/1) | Chốt giả thuyết, budget và schema dùng chung | Nguyễn Đình Phúc | 09:00 | **09:10** | — | Đã đóng |
| [#2](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/2) | Khởi tạo môi trường và mẫu dữ liệu tích hợp | Đoàn Tuấn Long | 09:00 | **09:20** | — | Đã đóng |
| [#3](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/3) | Chốt một provider LLM dùng được | Nguyễn Đình Phúc | 09:10 | **09:30** | #1 | Mở |
| [#4](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/4) | Tính cost và kiểm tra policy cơ bản | Nguyễn Việt Thành | 09:10 | **09:30** | #1 | Mở |
| [#5](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/5) | Sinh hai tập dữ liệu S0 cho demo | Đoàn Tuấn Long | 09:20 | **09:45** | #1, #2 | Mở |
| [#6](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/6) | Chọn baseline TTL chung ở 810 GB | Nguyễn Việt Thành | 09:30 | **09:45** | #4 | Mở |
| [#7](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/7) | Tính coverage bằng evaluator đơn giản | Đinh Ngọc Đức | 09:10 | **09:40** | #1, #2, #4 | Mở |
| [#8](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/8) | Grid search TTL cho một tập development | Nguyễn Việt Thành | 09:45 | **10:10** | #4, #5, #6, #7 | Mở |
| [#9](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/9) | Gọi LLM một lần để nhận xét metrics | Nguyễn Đình Phúc | 09:30 | **10:10** | #3 | Mở |
| [#10](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/10) | Xuất một HTML report dễ đọc mỗi eval | Đinh Ngọc Đức | 09:40 | **10:10** | #7, #9 | Mở |
| [#11](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/11) | Mô tả một failure case đơn giản | Đoàn Tuấn Long | 09:45 | **10:10** | #5, #7 | Mở |
| [#12](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/12) | Ghép một lệnh eval và lưu policy trước holdout | Nguyễn Việt Thành | 10:10 | **10:20** | #5, #6, #7, #8, #9, #10 | Mở |
| [#13](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/13) | Chạy một eval chính và lưu report thật | Đinh Ngọc Đức | 10:20 | **10:40** | #12 | Mở |
| [#14](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/14) | README ngắn và dàn ý 4 slide | Nguyễn Đình Phúc | 10:10 | **10:50** | #13 | Mở |
| [#15](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/15) | Chạy lại demo và kiểm tra HTML | Đoàn Tuấn Long | 10:40 | **10:55** | #13 | Mở |
| [#16](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues/16) | Đóng gói bộ demo tối thiểu | Đinh Ngọc Đức | 10:40 | **11:00** | #11, #14, #15 | Mở |

## Việc từng người

- **Thành (thanhnvhust514):** #4 cost, #6 baseline, #8 grid search, #12 ghép lệnh eval.
- **Long (tlong1610):** #5 dữ liệu main, #11 failure case, #15 kiểm tra lại; #2 đã đóng.
- **Đức (dinhngocduc1311):** #7 evaluator, #10 HTML, #13 eval thật, #16 bàn giao.
- **Phúc (rin1652):** #3 một provider, #9 nhận xét LLM, #14 README/pitch; #1 đã đóng.

Code Phúc đã có research notes, prompt và công cụ thử LLM; dùng lại trước khi viết thêm. Phần cost/baseline/generator đang triển khai chưa được tính là đã nghiệm thu. Nếu GitHub chưa cho gán Long, giữ người phụ trách trong body.

## Checklist từng issue đang mở

### #3 — Chốt một provider LLM dùng được

- [ ] Dùng research notes/prompt đã có; ghi tên provider/model và cách đặt key.
- [ ] Thử một lời gọi thật thành công; chốt timeout 30 giây.

**Đầu ra:** docs/research-notes.md, .env.example, prompt.

**Để sau:** Không cần so sánh nhiều provider/model hoặc mở rộng khảo sát tài liệu.

### #4 — Tính cost và kiểm tra policy cơ bản

- [ ] Viết cost = tổng history_gb_per_day × TTL; kiểm tra đủ 3 bảng, TTL hợp lệ, minimum và cost ≤ 810 GB.
- [ ] Kiểm tra tay cost 83/760/810 GB; policy vượt budget hoặc dưới minimum bị từ chối.

**Đầu ra:** src/cost_model.py và một nhóm test nhỏ.

**Để sau:** Không cần storage multiplier, cost phi tuyến hoặc mô hình engine thật.

### #5 — Sinh hai tập dữ liệu S0 cho demo

- [ ] Đọc config hiện có; sinh S0 development seed 1001 và holdout seed 2001, mỗi tập 900 incident (300/profile).
- [ ] Cùng seed/config cho cùng dữ liệu; ID và H=A+D+L đúng schema.
- [ ] Hỗ trợ S1 seed tương ứng cho một failure case nếu #11 cần; không thêm configs/profiles.json.

**Đầu ra:** src/generator.py; JSONL development/holdout.

**Để sau:** Không bắt buộc sinh cả 10 seed, S2/S3 hay làm thống kê phân phối chi tiết.

### #6 — Chọn baseline TTL chung ở 810 GB

- [ ] Chọn TTL chung lớn nhất trong grid thỏa minimum và budget, chỉ đọc config.
- [ ] Xuất TTL 30/30/30, cost 810 GB; kiểm tra một budget thấp để báo infeasible.

**Đầu ra:** src/policies.py; baseline JSON.

**Để sau:** Không bắt buộc sweep budget hoặc Pareto.

### #7 — Tính coverage bằng evaluator đơn giản

- [ ] Hàm recovery: không mất hạ tầng và H≤TTL; mẫu số giữ mọi incident.
- [ ] Trả recoverable/total/coverage và cost cho từng policy; so hai policy trên cùng incident.
- [ ] Dùng 7 fixture đã có để kiểm tra boundary, infra-loss và policy invalid.

**Đầu ra:** src/evaluator.py và test fixture.

**Để sau:** Chưa cần CSV, aggregate nhiều seed, interval hoặc toàn bộ metric phụ.

### #8 — Grid search TTL cho một tập development

- [ ] Duyệt 216 vector grid, bỏ policy vi phạm minimum/budget, tối đa coverage trên S0 dev1001.
- [ ] Tie-break: cost thấp hơn, rồi vector TTL theo thứ tự profile; không đọc holdout.
- [ ] Trả policy TTL/cost/feasible; báo infeasible nếu không có ứng viên.

**Đầu ra:** Hàm optimize trong src/policies.py.

**Để sau:** Không cần thuật toán mới, nhiều budget hoặc huấn luyện nhiều seed.

### #9 — Gọi LLM một lần để nhận xét metrics

- [ ] Hàm nhận metrics và gọi một provider đang dùng được, tạo 3–5 câu tiếng Việt.
- [ ] LLM chỉ diễn giải metric thật; lưu model, response và trạng thái.
- [ ] Lỗi/timeout thì trả status error để HTML vẫn xuất; không tạo nhận xét giả.

**Đầu ra:** src/llm_commentary.py.

**Để sau:** Không cần nhiều provider, retry phức tạp, streaming hoặc framework agent.

### #10 — Xuất một HTML report dễ đọc mỗi eval

- [ ] Tạo reports/<run_id>/report.html và metrics.json; run_id timestamp + UUID, không ghi đè.
- [ ] HTML offline có bảng baseline/optimized: TTL, budget, cost, coverage và delta điểm phần trăm.
- [ ] Có 3–5 câu LLM và status; khi LLM lỗi hiển thị rõ thiếu nhận xét.

**Đầu ra:** src/report.py; HTML và JSON.

**Để sau:** Biểu đồ, dashboard, template engine và CSV đều tùy chọn.

### #11 — Mô tả một failure case đơn giản

- [ ] Dùng S1 infra-loss đã có: 24/300 incident mất hạ tầng mỗi profile, TTL lớn vẫn không cứu được.
- [ ] Nếu chạy eval S1: học riêng trên S1 dev1001 rồi dùng S1 holdout2001; hai policy cùng dữ liệu.
- [ ] Viết 2–3 câu giải thích giới hạn time travel không thay backup; tách kết quả S1 khỏi S0.

**Đầu ra:** Một đoạn failure case trong README/report; không cần file scenario mới.

**Để sau:** S2 tail shift và S3 slow response để sau MVP; không chặn demo S0.

### #12 — Ghép một lệnh eval và lưu policy trước holdout

- [ ] Ghép generator → baseline/optimizer trên development → lưu policy → evaluator holdout → LLM → HTML.
- [ ] Lưu config, policy, seed, budget và config hash trong thư mục run; không sửa TTL sau khi đọc holdout.
- [ ] Có một lệnh chạy demo S0 ở budget 810 GB; ghi rõ execution_scope=mvp và selected_runs.

**Đầu ra:** python -m src.run_eval --config configs/experiment.sample.json; policy/config/metrics/report.

**Để sau:** Không cần orchestration framework, policy registry hoặc khóa nhiều seed.

### #13 — Chạy một eval chính và lưu report thật

- [ ] Chạy S0 dev1001 → holdout2001 tại 810 GB; lưu policy, metrics.json và report.html có LLM thật.
- [ ] Ghi coverage hai policy và delta đúng kết quả, kể cả khi không cải thiện.
- [ ] Chạy thêm S1 cho failure case khi đã sẵn sàng, lưu tách biệt; báo limitation một seed.

**Đầu ra:** Một thư mục run hoàn chỉnh; kết quả cho README/pitch.

**Để sau:** 10 seed, mean/std, budget sweep và Pareto để sau MVP.

### #14 — README ngắn và dàn ý 4 slide

- [ ] README có setup, một lệnh eval, đường dẫn report và bảng kết quả thật.
- [ ] Ghi một failure case, giới hạn mô phỏng và chỉ chạy một seed.
- [ ] Dàn ý tối đa 4 slide Pain/Method/Evidence/Decision; link run thật.

**Đầu ra:** README.md; docs/pitch-outline.md.

**Để sau:** Không cần slide thiết kế cầu kỳ, video hoặc báo cáo dài.

### #15 — Chạy lại demo và kiểm tra HTML

- [ ] Chạy lệnh eval hai lần trên môi trường đã cài; xác nhận hai thư mục report riêng.
- [ ] Metric/TTL/cost tái lập cùng config/seed; text LLM có thể khác nhau.
- [ ] Mở HTML và đối chiếu số với JSON; ít nhất một run có LLM thật thành công.

**Đầu ra:** docs/verification.md với lệnh và pass/fail.

**Để sau:** Không bắt buộc máy thứ hai, venv thứ ba hoặc ma trận nhiều hệ điều hành.

### #16 — Đóng gói bộ demo tối thiểu

- [ ] Có code/config, README, JSON metrics, HTML có LLM và dàn ý tối đa 4 slide.
- [ ] Kiểm tra 3 profile, 900 incident/tập, development/holdout riêng, cùng budget và một failure case.
- [ ] Đưa commit và link artifact vào issue; ghi hạn chế/chỗ chưa làm.

**Đầu ra:** Link commit và thư mục evidence đã chọn.

**Để sau:** Không cần CI, container, deploy web hoặc dashboard.

## Bàn giao đơn giản

Đưa commit hoặc file đầu ra, lệnh chạy và kết quả thật vào issue. Người kiểm tra rà nhanh; chỉ đóng khi đạt checklist, không ghi người khác đã review khi chưa có xác nhận. Không bắt buộc thêm quy trình hoặc tài liệu nghiệm thu dài.

## Checklist bộ nộp

- [ ] Hai tập S0 development/holdout riêng, 3 profile, 900 incident/tập.
- [ ] Baseline và optimized cùng budget/cost model, không tune theo holdout.
- [ ] Có metric thật, một failure case, HTML từng eval và LLM thật.
- [ ] Chạy lại metric/TTL/cost tái lập; report khớp JSON.
- [ ] README, config/code, artifacts và tối đa 4 slide.

Một seed là giới hạn của demo; chưa có kết luận thống kê hoặc Pareto. Yêu cầu HTML và LLM là yêu cầu người dùng bổ sung từ hướng dẫn của thầy. Deadline và cách chia issue là đề xuất kế hoạch.

Issue #1/#2 giữ bằng chứng lịch sử tại [review #1](issue-01-review.md) và [review #2](issue-02-review.md); checklist còn lại không chứng nhận công việc đã xong.


