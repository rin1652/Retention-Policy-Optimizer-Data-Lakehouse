# Hiểu bài toán: Retention Policy Optimizer

**Với cùng ngân sách lưu trữ, mỗi loại bảng nên giữ lịch sử bao lâu để khôi phục được nhiều sự cố nhất?**

```mermaid
flowchart TD
    A["Có 3 loại dữ liệu<br/>Dữ liệu thô · Dữ liệu nghiệp vụ · Dữ liệu huấn luyện AI"]
    B["Ngân sách lưu trữ có giới hạn"]
    C["Cách hiện tại<br/>Mọi bảng giữ lịch sử cùng số ngày"]
    D["Cách nhóm đề xuất<br/>Mỗi loại bảng giữ lịch sử số ngày phù hợp"]
    E["Thử trên cùng các sự cố<br/>Dữ liệu bị sửa sai, nhưng lỗi được phát hiện muộn"]
    F{"Khi cần khôi phục<br/>bản dữ liệu sạch còn đọc được không?"}
    G["Có → Khôi phục được"]
    H["Không → Không khôi phục được"]
    I["So sánh hai cách<br/>Cách nào khôi phục được nhiều sự cố hơn<br/>mà vẫn trong cùng ngân sách?"]

    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    E --> F
    F -->|Có| G
    F -->|Không| H
    G --> I
    H --> I

    classDef context fill:#eff6ff,stroke:#2563eb,color:#0f172a;
    classDef policy fill:#fff7ed,stroke:#ea580c,color:#0f172a;
    classDef success fill:#ecfdf5,stroke:#059669,color:#0f172a;
    classDef failure fill:#fef2f2,stroke:#dc2626,color:#0f172a;
    class A,B,E,F context;
    class C,D policy;
    class G,I success;
    class H failure;
```

## Ví dụ dễ hiểu

Dữ liệu bị sửa sai hôm thứ Hai, đến thứ Sáu mới phát hiện. Nếu bản sạch trước lỗi vẫn còn đọc được thì có thể phục hồi; nếu đã bị dọn thì không.

Giữ lịch sử lâu hơn có thể tăng khả năng phục hồi nhưng tốn thêm dung lượng. Nhóm cần **chia ngân sách hợp lý giữa các loại bảng**, rồi đo tỷ lệ sự cố khôi phục được.

## Nhóm cần chứng minh điều gì?

- Hai cách dùng **cùng ngân sách** và được thử trên **cùng sự cố**.
- Cách đề xuất chọn thời gian giữ riêng cho từng loại bảng, thay vì một thời gian chung.
- Kết quả chính là **tỷ lệ sự cố khôi phục được**: số sự cố khôi phục được chia cho tổng số sự cố.
- Nếu cách đề xuất không tốt hơn, nhóm vẫn báo cáo kết quả thật và giải thích khi nào phương pháp thất bại.

Giữ lịch sử không thay thế backup: nếu mất toàn bộ nơi lưu dữ liệu và lịch sử, tăng số ngày giữ cũng không tạo ra một bản sao độc lập để phục hồi.

Sau khi đo, hệ thống xuất **report HTML** có bảng, biểu đồ và vài câu **nhận xét LLM**. LLM giúp giải thích kết quả; metric được tính bằng code đánh giá.

## Đọc tiếp

- [Sơ đồ triển khai và vai trò từng người](workflow.md)
- [Kế hoạch issue và deadline](issue-plan.md)
- [Tóm tắt tài liệu và phân tích đề tài 5](lakehouse-summary-topic-5.md)
