# Phạm vi MVP — làm nhanh, dễ ghép, dễ demo

Cập nhật 04/10/2026 theo yêu cầu người dùng giảm độ phức tạp issue. Đây là quyết định về phạm vi triển khai của nhóm; không phải thông báo thay đổi yêu cầu của giảng viên.

## Bản demo cần đạt

Một lệnh eval sinh dữ liệu, chọn baseline và tối ưu bằng development, lưu policy trước holdout, tính metric, gọi LLM và xuất HTML. Giữ mô phỏng Python; dùng code/config hiện có.

- Ba profile và cost tuyến tính giữ nguyên: raw 20/min1, curated 5/min7, training 2/min14.
- Budget duy nhất **810 GB history overhead**; grid giữ [1,7,14,30,60,90].
- Main: **S0 development1001 → holdout2001**, 300 incident/profile, **900/tập**.
- Baseline chung 30 ngày, cost 810 GB; grid search TTL riêng trên 216 vector, chỉ đọc development.
- Recovery: không mất hạ tầng và H≤TTL, với H=A+D+L. Hai policy dùng cùng incident holdout.
- Một failure case S1: nếu chạy đo, học riêng trên S1 dev1001 → S1 holdout2001; 24/300 incident mất hạ tầng mỗi profile. Không trộn S1 vào metric chính S0.
- Mỗi eval có một thư mục run mới chứa config, policies, metrics.json, report.html và nhận xét LLM 3–5 câu.
- HTML chỉ cần bảng dễ đọc, TTL/cost/coverage/delta và phần LLM. Nếu LLM lỗi vẫn xuất HTML ghi error; nghiệm thu phần LLM cần một run gọi thật thành công.

## Cắt phần mở rộng khỏi checklist bắt buộc

Không bắt buộc 10 seed, mean/std/CI, budget sweep/Pareto, S2/S3, dashboard, biểu đồ, CSV, container/CI hoặc nhiều provider LLM. Không cần thêm profiles.json/scenarios.json: đọc **configs/experiment.sample.json**.

Chỉ cần kiểm tra đáp án tính tay của cost, baseline, recovery boundary, mất hạ tầng và một lần chạy pipeline. Dùng fixture/test có sẵn; không viết thêm ma trận test nếu không cần.

## Quan hệ với contract v1.0

[Contract v1.0](experiment-contract.md) tiếp tục quy định profile, schema, RNG, cost, boundary và tie-break. MVP này thay **phạm vi chạy và tiêu chí nghiệm thu**: chọn một cặp seed và một budget từ config, thay vì chạy hết toàn bộ seeds/scenarios/sweep trong config. Những danh sách đó là các lựa chọn đã khai báo cho bản đầy đủ.

Ghi execution_scope=mvp và selected_runs trong metadata/report để thấy rõ đã chạy phần nào. Lưu config nguyên bản và hash; không ghi đã chạy 10 seed hay kết luận thống kê nhiều lần lặp. Không sửa tham số sau khi xem holdout. Kết quả một seed chỉ là demo ban đầu.

Issue #1/#2 đã đóng giữ nguyên bằng chứng lịch sử. Tài liệu/review trước đây về venv và phiên bản mô tả lần chạy trước, không chứng nhận tự động cho dependency LLM Phúc vừa bổ sung.

## Phân công gọn

| Người | Việc cần hoàn thành |
|---|---|
| Thành | cost → baseline → grid search → một lệnh ghép pipeline |
| Long | hai tập dữ liệu main → hỗ trợ S1 → chạy lại/kiểm tra |
| Đức | evaluator → HTML → chạy eval → gom bộ nộp |
| Phúc | chọn một LLM dùng được → nhận xét metrics → README và 4 slide |

Giữ các issue hiện có để tránh đổi link/dependency. Mỗi issue có 2–3 bước và một đầu ra. Người kiểm tra chỉ rà nhanh bằng lệnh/kết quả thực; không thêm quy trình phê duyệt hoặc checklist dài.

## Lịch đề xuất

Giữ lịch **05/10/2026 09:00–11:00 UTC+7** và các deadline trong [issue-plan.md](issue-plan.md). Đây vẫn là lịch đề xuất chưa được nhóm xác nhận, không phải hạn nộp do thầy công bố.

## Điều kiện hoàn thành demo

- [ ] S0 main chạy trên hai tập riêng, cùng budget và dữ liệu cho hai policy.
- [ ] Có metrics thật và một failure case được giải thích.
- [ ] Mỗi eval có HTML mới; có run với 3–5 câu LLM thật.
- [ ] Chạy lại cho metric/TTL/cost giống nhau; text LLM có thể khác.
- [ ] README có setup, một lệnh eval và link artifacts; tối đa 4 slide.

Chưa có kết quả demo được nghiệm thu chỉ vì đã rút gọn kế hoạch.

