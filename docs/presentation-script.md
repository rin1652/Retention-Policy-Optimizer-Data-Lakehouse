# Kịch bản Thuyết trình: Retention Policy Optimizer

**Thời lượng dự kiến:** 5 - 7 phút
**Công cụ hỗ trợ:** Giao diện React Dashboard (`http://localhost:5173/`)

---

## 1. Mở đầu & Giới thiệu Vấn đề (1.5 phút)

*(Mở trình duyệt, show dashboard tổng quan)*

**Chào mọi người,**
Hôm nay nhóm chúng em xin trình bày về Đề tài số 5: **Tối ưu hóa chính sách lưu giữ dữ liệu (Retention Policy) cho Data Lakehouse.** 

Như mọi người đều biết, các hệ thống như Delta Lake hay Iceberg cho phép chúng ta "quay ngược thời gian" (Time Travel) để cứu dữ liệu nếu có lỗi xảy ra. Tuy nhiên, hiện tại hầu hết các công ty đang dùng một **cách tiếp cận rất lười biếng (One-size-fits-all)**: Đó là set chung một mức thời gian, ví dụ 30 ngày cho TẤT CẢ các bảng dữ liệu.

Nhìn vào phần **Benchmarks & Thông số Mô phỏng** (chỉ tay vào Dashboard), ta thấy sự bất cập rất lớn:
- Bảng **Raw Ingest** mỗi ngày sinh ra 20GB. Nếu có lỗi, team Data Engineer phát hiện ngay trong 1-2 ngày. Giữ 30 ngày là **vung tiền qua cửa sổ**.
- Trong khi đó, bảng **Training Dataset** chỉ sinh ra 2GB/ngày. Nhưng nếu model AI bị ngộ độc dữ liệu, Data Scientist mất tới 1-2 tháng mới phát hiện ra. Giữ 30 ngày là **quá ngắn, dữ liệu bị xoá sạch trước khi kịp cứu**.

$\Rightarrow$ **Nghịch lý là:** Chỗ không cần thì tốn đống tiền để giữ, chỗ sinh tử thì lại mất phao cứu sinh!

---

## 2. Giải pháp & Cách tiếp cận (1.5 phút)

Để giải quyết vấn đề này, nhóm em đã xây dựng một **Trình mô phỏng (Data Simulator) và Thuật toán Tối ưu (Policy Optimizer)**.

- **Về Mô phỏng:** Chúng em giả lập 900 sự cố phân bổ đều trên 3 loại bảng, với độ trễ phát hiện (Delay) đúng theo thực tế: Raw thì ngắn, Training thì dài. Có cả 8% tỷ lệ mất trắng hạ tầng (để chứng minh Time Travel không phải là Backup).
- **Về Tối ưu:** Dưới một ngân sách cố định là 810 GB. Thuật toán của chúng em sẽ quét qua tất cả các cấu hình (Grid Search) để tìm ra bộ ngày (TTL) cho TỪNG BẢNG sao cho tỷ lệ khôi phục (Recovery Coverage) là CAO NHẤT.

Và đây là kết quả! *(Cuộn lên phần Thẻ (Card) hiển thị số liệu)*

---

## 3. Trình diễn Kết quả & Số liệu (2 phút)

*(Chỉ vào Bảng So sánh Cấu hình đang nhấp nháy)*

Mọi người hãy nhìn vào bảng So Sánh này:
- Ở dòng **Baseline**, với cấu hình đồng loạt 30 ngày cho tất cả các bảng, chi phí chạm ngưỡng 810GB. Khả năng khôi phục chỉ đạt khoảng **81.2%**.
- Nhưng ở dòng **Optimized (Giải pháp của chúng em)**: Chúng em quyết định **cắt giảm** bảng Raw Ingest xuống chỉ còn 7 ngày *(chỉ vào ô 7 ngày màu đỏ nhấp nháy)*. Lượng dung lượng khổng lồ được giải phóng sẽ được **đắp sang** bảng Training Dataset, nâng nó lên tới tận 60 ngày *(chỉ vào ô 60 ngày màu xanh)*!

*(Chỉ lên các thông số Metric chính)*
Kết quả là gì? Vẫn với đúng **810GB** tiền server đó, chúng em đã tăng tỷ lệ cứu dữ liệu (Coverage) từ 81.2% lên tận **94.5%**! Mức chênh lệch là **+13.3 điểm %**. 

Toàn bộ những sự cố thảm họa phát hiện muộn ở team AI (trong khoảng 30-60 ngày) đều được cứu sống hoàn toàn.

*(Chỉ vào Box Phân tích AI)*
Và để tự động hoá việc báo cáo, chúng em đã tích hợp gọi **AI LLM (DeepSeek-V4-Flash)** để đọc số liệu và tự động sinh ra lời nhận xét này cho Ban giám đốc, giúp họ đưa ra quyết định mà không cần nhìn vào đống số liệu khô khan.

---

## 4. Ràng buộc & Tổng kết (1 phút)

*(Cuộn xuống phần Tiêu chí & Ràng buộc)*

Tuy kết quả rất tốt, nhưng phương pháp này vẫn phải tuân thủ nghiêm ngặt các rào cản kỹ thuật:
1. Thứ nhất, thuật toán đã bị trừ đi các trường hợp **Infra Loss (Xoá nhầm Bucket)**. Nếu mất Bucket, TTL 60 ngày cũng vô dụng. Phải có Disaster Recovery riêng.
2. Thứ hai, sự tối ưu này phụ thuộc vào hành vi của team. Nếu team Data đổi quy trình, ta cần chạy lại Pipeline này để tìm ra con số TTL mới.

**Tóm lại:** Việc tinh chỉnh TTL theo từng profile bảng (Per-profile Retention) tốn thêm một bước Setup, nhưng mang lại lợi ích kép khổng lồ: Tăng tính an toàn mạng lưới AI lên mức cao nhất mà không làm phình to hóa đơn Cloud.

Đó là toàn bộ phần demo của nhóm em. Các tiêu chí chấm điểm khắt khe đều đã được pass thành công. Cảm ơn mọi người đã lắng nghe!
