# Retention-Policy-Optimizer-Data-Lakehouse

Đề tài #5: tối ưu retention theo nhóm bảng để tăng RecoveryCoverage ở cùng ngân sách lưu trữ lịch sử.

## Tài liệu

- [Bắt đầu tại đây: sơ đồ giải thích bài toán](docs/problem-overview.md)
- [Sơ đồ luồng đơn giản và vai trò từng người](docs/workflow.md)
- [Tóm tắt PDF và phân tích đề tài 5](docs/lakehouse-summary-topic-5.md)
- [Kế hoạch phân công, deadline và 16 issue](docs/issue-plan.md)
- [GitHub Issues](https://github.com/rin1652/Retention-Policy-Optimizer-Data-Lakehouse/issues)

## Nhóm

| Thành viên | GitHub | Phần việc |
|---|---|---|
| Nguyễn Đình Phúc | rin1652 | Mô hình, nghiên cứu, LLM, README/pitch |
| Đoàn Tuấn Long | tlong1610 | Môi trường, dữ liệu, scenario, tái lập |
| Nguyễn Việt Thành | thanhnvhust514 | Cost model, baseline, optimizer, khóa policy |
| Đinh Ngọc Đức | dinhngocduc1311 | Evaluator, HTML report, eval, bộ nộp |

Kế hoạch issue cụ thể hóa phân công hiện tại; Phúc phụ trách client LLM và Đức tích hợp vào report. Tại lúc lập kế hoạch, tài khoản Long chưa đủ điều kiện assignee của repo; người phụ trách vẫn được ghi trong 4 issue của Long.

## Lịch đề xuất và đầu ra

Sprint đề xuất **05/10/2026, 09:00–11:00, giờ Việt Nam (UTC+7)**. Nhóm chưa xác nhận giờ bắt đầu/nộp; đây không phải deadline do giảng viên công bố.

Prototype dự kiến so sánh TTL chung với TTL theo profile trên development/holdout riêng. Mỗi lần chạy eval phải xuất report HTML có bảng/biểu đồ và 3–5 câu nhận xét LLM dựa trên số liệu thật.

Repo hiện chứa tài liệu và issue kế hoạch; code mô phỏng, report và kết quả thực nghiệm sẽ được bổ sung theo các issue. Hướng dẫn chạy sẽ được cập nhật khi prototype hoàn thành.


