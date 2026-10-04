# Research Notes (TASK-03)

## Delta Lake
Time travel là đọc lại snapshot/version cũ. Muốn time travel được thì phải còn cả log và data files tương ứng. VACUUM xóa các data file cũ; sau khi file cần thiết bị vacuum thì không thể time travel về version đó nữa. Delta mặc định khuyến nghị retention VACUUM tối thiểu khoảng 7 ngày để tránh ảnh hưởng reader/writer đang chạy. [Delta Lake](https://docs.delta.io/delta-batch/?utm_source=chatgpt.com)

## Apache Iceberg
Mỗi lần ghi tạo một snapshot. Snapshot có thể dùng để time travel hoặc rollback. Khi expireSnapshots, snapshot cũ bị loại khỏi metadata và không còn dùng được cho time travel; các file không còn được snapshot nào tham chiếu mới có thể bị xóa. [Apache Iceberg](https://iceberg.apache.org/docs/nightly/maintenance/?utm_source=chatgpt.com)

## Phân biệt
- **Time travel** = đọc lại dữ liệu ở version cũ.
- **Rollback** = đưa trạng thái hiện tại của table quay về snapshot/version cũ. Iceberg có API rollback trực tiếp theo snapshot hoặc thời gian. [Apache Iceberg](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/ManageSnapshots.html?utm_source=chatgpt.com)
- **Backup** = bản sao độc lập khỏi failure domain hiện tại. Time travel/rollback không phải backup; nếu storage/hạ tầng chứa cả current data và history bị mất thì retention không cứu được.

## Giới hạn simulator
Bài của nhóm chỉ dùng:
`cost = Σ(history_gb_per_day × TTL)`

Đây là mô hình cost tuyến tính để so policy, không mô phỏng đầy đủ storage engine thực tế.
TTL trong simulator chỉ là biến thí nghiệm, không được hiểu là cấu hình VACUUM/expire snapshots thật. Trong production, retention còn phụ thuộc concurrent transactions, stream lag, snapshot references, log retention và policy vận hành thực tế. Delta cũng cảnh báo retention quá ngắn có thể làm reader/writer lỗi hoặc thậm chí gây corruption. [Delta Lake](https://docs.delta.io/delta-utility/?utm_source=chatgpt.com)

## LLM nên chọn gì
Nếu chỉ dùng LLM để đọc metrics và viết nhận xét 3–5 câu, em chọn:
- **Provider:** OpenAI
- **API:** Responses API
- **Model:** gpt-6-luna

**Lý do:** task rất nhẹ, không cần model mạnh; Luna là model chi phí thấp trong bảng giá hiện tại. OpenAI hiện khuyến nghị dùng Responses API cho integration mới. [OpenAI Platform](https://platform.openai.com/pricing?client_id=81433148.1787961602&session_id=1787961602&utm_source=chatgpt.com)

**Credential:**
```bash
export OPENAI_API_KEY="..."
```
Code đọc key từ biến môi trường, không commit API key lên Git.

**Prompt ngắn:**
> Given the experiment metrics below, summarize the result in 3–5 sentences. Compare the optimized per-profile TTL policy with the uniform-TTL baseline. Mention RecoveryCoverage, storage cost, and any failure case. Do not invent explanations that are not supported by the metrics.

## Timeout và lỗi
Chốt đơn giản:
`timeout = 30 seconds`

Nếu LLM lỗi/timeout:
- experiment vẫn hợp lệ vì metric được tính bằng code, không phải LLM;
- ghi `llm_status = "error"` hoặc `"timeout"`;
- lưu message lỗi;
- report vẫn xuất metrics bình thường, chỉ thiếu phần nhận xét LLM.

Điểm quan trọng nhất: LLM chỉ giải thích kết quả, không được quyết định TTL và không được tính metric.
