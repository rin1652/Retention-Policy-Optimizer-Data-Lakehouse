# Pitch Deck Outline: Retention Policy Optimizer

Bài trình bày (pitch) này gồm 4 slide đúng tiêu chuẩn tóm tắt đề tài.

## Slide 1: Pain (Vấn đề & Nỗi đau)
- **Tình huống:** Các data lakehouse hiện đại (Delta/Iceberg) giữ history files cho tính năng time-travel. Nhưng thiết lập một khoảng thời gian (TTL) **đồng nhất cho tất cả các bảng** (ví dụ: 30 ngày) gây lãng phí nghiêm trọng.
- **Nỗi đau 1 - Phá ngân sách lưu trữ:** Bảng Raw Ingest chiếm 80% dung lượng mỗi ngày nhưng lại hiếm khi lỗi logic khó sửa. Giữ 30 ngày ngốn lượng tài nguyên khổng lồ.
- **Nỗi đau 2 - Mất khả năng phục hồi:** Bảng Training/Curated cực kì quan trọng nhưng khi model hỏng hóc hoặc có sự cố, thường mất đến nhiều tuần để phát hiện. TTL 30 ngày là **quá ngắn**, dẫn đến dữ liệu bị VACUUM/expire trước khi kỹ sư kịp cứu.
- **Nghịch lý:** Chúng ta vừa vung tiền qua cửa sổ, vừa không có phao cứu sinh lúc cần thiết.

## Slide 2: Approach (Giải pháp & Tiếp cận)
- **Cốt lõi:** Phân bổ TTL dựa trên Rủi ro & Tầm quan trọng của từng Profile. Chuyển bài toán thành một dạng "Tối ưu hóa Coverage" (Khả năng che phủ rủi ro) dưới một mốc "Ngân sách lưu trữ" (Storage Budget) cố định.
- **Mô hình hóa Hồ sơ (Profiles):**
  - *Raw Ingest*: Lưu lượng ghi lớn, độ trễ phát hiện lỗi ngắn (1-2 ngày). TTL chỉ cần 7 ngày.
  - *Curated Business*: Ghi trung bình, trễ trung bình. TTL cần ~30 ngày.
  - *Training Dataset*: Ghi rất ít, trễ cực lâu (30-60 ngày). Cần TTL dài (đến 60 ngày).
- **Thuật toán Tối ưu:** Sử dụng Exhaustive Grid Search qua hàng ngàn giả lập độ trễ lỗi (Detect Delay, Response Lag) để tìm ra bộ TTL cho phép số lượng sự cố nằm trong "Vùng an toàn" (Target Age $\le$ TTL) là cực đại.

## Slide 3: Evidence (Bằng chứng & Số liệu)
- **Cấu hình thí nghiệm:** Đánh giá trên 900 sự cố phân bổ trên 3 bảng. Cố định Budget = 810 GB.
- **Kết quả Baseline (Uniform TTL = 30 ngày):**
  - Tiêu tốn 810GB.
  - Raw Ingest dư thừa bảo vệ. 
  - Training Dataset bị mất trắng những lỗi phát hiện sau ngày 30.
- **Kết quả Optimized (TTL = 7, 30, 60 tương ứng):**
  - Vẫn dùng đúng 810GB (Cost Neutral).
  - Tăng vọt Recovery Coverage tổng thể. 100% sự cố trên Training Dataset (thường delay 30-60 ngày) được cứu sống, trong khi mảng Raw Ingest (delay < 7 ngày) không hề hấn gì. 
  - Có đường ranh giới chênh lệch (Delta PP) chứng minh Optimized luôn vượt trội ở cùng mức phí.

## Slide 4: Decision & Risk (Quyết định & Rủi ro)
- **Hành động (Decision):** Áp dụng ngay bộ cấu hình TTL phân mảnh theo profile. Cấu hình tự động tham số `VACUUM RETAIN` (Delta) và `expire_snapshots` (Iceberg) cho các lớp dữ liệu.
- **Rủi ro Cảnh báo (Risk):**
  - Mất hạ tầng vật lý (Infrastructure Loss): Time-travel / Retention không thay thế cho Backup / Disaster Recovery. Giữ TTL 100 ngày cũng vô dụng nếu S3 Bucket bị xóa. Phải kết hợp thêm Cross-region replication.
  - Dịch chuyển phân phối lỗi (Shift): Nếu dev phản hồi chậm đột ngột (Response Lag tăng lên cực hạn), TTL 7 ngày có thể bị chọc thủng. 
- **Bước tiếp:** Triển khai chạy mô phỏng định kỳ hàng quý để auto-tune lại TTL theo nhịp độ phát sinh dữ liệu mới.
