# Retention Policy Optimizer - Data Lakehouse

Dự án này là hệ thống thiết kế và tối ưu chính sách lưu giữ dữ liệu (Retention Policy) cho các nhóm bảng (profiles) trong Data Lakehouse (vd: Delta Lake, Apache Iceberg) nhằm cân bằng giữa chi phí lưu trữ (Storage Cost) và khả năng phục hồi dữ liệu khi có sự cố (Recovery Coverage).

## Bài toán & Động lực
Một quy tắc "30 ngày" cho mọi bảng hiếm khi tối ưu.
- **Bảng raw ingest**: Khối lượng dữ liệu cực lớn, tần suất ghi cao. Rất hiếm khi cần time travel quá vài ngày vì có thể chạy lại data pipeline gốc.
- **Bảng training dataset / Curated**: Dữ liệu quý giá, quá trình tạo tốn kém và không dễ tái lập. Phát hiện lỗi có thể chậm (sau vài tuần model suy giảm hiệu suất mới phát hiện ra).
=> Cần thiết lập **TTL riêng rẽ** theo từng profile bảng.

## Tính năng (Features)
- **Data Simulator** (`src/simulate.py` / `src/generator.py`): Mô phỏng hàng ngàn sự cố mất/sai lệch dữ liệu với độ trễ phát hiện (Detect Delay) được phân phối theo đặc thù từng nhóm bảng. Hỗ trợ mô phỏng mất hạ tầng (Infrastructure Loss).
- **Policy Optimizer** (`src/policies.py`): Chạy lưới tìm kiếm toàn diện (Exhaustive Grid Search) trên tập Development để tìm bộ tham số TTL theo từng bảng mang lại Recovery Coverage cao nhất trong khi không vượt qua ngân sách Storage (Budget). 
- **Evaluator độc lập** (`src/evaluate.py`): Đánh giá chính sách TTL trên tập Holdout/Shift. Mô hình tuân thủ quy tắc nghiêm ngặt: $H \le TTL$ và không bị Infrastructure Loss mới được tính là phục hồi thành công.
- **HTML Reporter & LLM Commentary** (`src/report.py`, `src/llm_commentary.py`): Xuất kết quả đối chiếu giữa Baseline và Optimized kèm theo nhận xét tự động từ AI (hỗ trợ OpenAI/FPT/Gemini).

## Cài đặt & Chạy thí nghiệm

1. Tạo biến môi trường:
```bash
cp .env.example .env
# Chỉnh sửa file .env với API Key (FPT hoặc Gemini)
```

2. Cài đặt thư viện:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Chạy Pipeline mô phỏng và tối ưu:
```bash
PYTHONPATH=. python src/main.py
```
> Kịch bản mặc định sử dụng 3 bảng cấu hình (`raw_ingest`, `curated_business`, `training_dataset`), tổng Storage Budget = 810GB. Baseline sử dụng TTL đồng đều cho mọi bảng (30 ngày). 

4. Xem Báo cáo:
Mở các file `reports/<run_id>/report.html` trên trình duyệt để đối chiếu biểu đồ/bảng số liệu coverage và cost.

## Cấu trúc Thư mục
- `configs/config.json` - (được đổi tên hoặc sao chép từ experiment.sample.json) File cấu hình JSON mô tả profiles, scenarios.
- `src/` - Chứa mã nguồn mô phỏng, tối ưu và đánh giá.
- `tests/` - Unit tests cho logic đánh giá.
- `reports/` - Output HTML và JSON sau mỗi lần chạy.
- `prompts/` - Mẫu prompt dùng cho LLM diễn giải.
- `docs/` - Tài liệu research và hợp đồng thiết kế.
