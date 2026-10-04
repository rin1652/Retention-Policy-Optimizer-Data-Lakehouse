# Data Lakehouse Open Research Challenge: Tóm tắt và phân tích đề tài 5

**Nguồn chính:** `lakehouse-open-research-challenges-student-brief.pdf`, 23 trang, do người dùng cung cấp.  
**Ngày biên soạn:** 04/10/2026.  
**Cách xác định đề tài:** Đề tài **#5 trong bảng chọn chủ đề ở trang 3** là **Retention Policy Optimizer**, trình bày ở trang 12–13, dưới tiêu đề mục **9**. Mục **5** trong bố cục tài liệu là AI Coding Agent as a Lakehouse Operator, tức đề tài #1. Bản phân tích này dùng số thứ tự đề tài trong bảng chọn chủ đề.

Phần I tóm tắt yêu cầu của tài liệu. Phần II phân biệt yêu cầu gốc với diễn giải và đề xuất nghiên cứu. Những yêu cầu nộp bài trong PDF được trình bày như nội dung cần hiểu; bản Markdown này không phải một báo cáo thí nghiệm đã thực hiện. Mọi số liệu minh họa dưới đây là giả định, không phải kết quả đo.

## I. Tóm tắt toàn bộ tài liệu

### 1. Mục tiêu và tinh thần của thử thách

Đây là một đợt nghiên cứu thực hành kéo dài **2 giờ**: chọn một vấn đề thật của lakehouse, tìm hiểu cách xử lý hiện có, xây dựng thí nghiệm hoặc mô phỏng tối thiểu, rồi cải thiện chỉ số được giao mà vẫn bảo đảm tính đúng đắn.

Lakehouse kết hợp lưu trữ dữ liệu theo kiểu data lake với các khả năng quản lý bảng như giao dịch, schema và lịch sử phiên bản. Các vấn đề trong đề bài xoay quanh ba nhóm: hiệu năng/chi phí, độ tin cậy/tính đúng đắn, và cách đánh giá hệ thống.

Tài liệu đánh giá cao **giả thuyết rõ ràng, baseline công bằng, bằng chứng có thể chạy lại và phân tích thất bại trung thực**. Hệ thống phức tạp hơn chưa chắc có giá trị nghiên cứu cao hơn.

### 2. Quy tắc làm nghiên cứu

- Bắt đầu từ giả thuyết, không bắt đầu từ việc chọn công cụ.
- Luôn so sánh với một phương pháp đơn giản làm **baseline**.
- Dùng kịch bản development để thiết kế/tinh chỉnh; giữ ít nhất một kịch bản **held-out** để kiểm tra khả năng khái quát khi có thể.
- Kiểm soát dataset, tài nguyên tính toán, cache, phiên bản engine và workload khi so sánh.
- Báo cáo ít nhất một tình huống phương pháp không có lợi hoặc thất bại.
- Có thể dùng AI coding agent, nhưng nhóm chịu trách nhiệm kiểm chứng code/SQL và bảo vệ tính toàn vẹn dữ liệu.
- Các phép thử bảo trì có khả năng phá hủy chỉ chạy trên bảng dùng một lần hoặc sandbox.
- **Không chấp nhận bài chỉ có slide:** phải có thí nghiệm hoặc mô phỏng đo được.

### 3. Bộ sản phẩm cần nộp theo tài liệu

| Thành phần | Nội dung |
|---|---|
| README khoảng 1 trang | Vấn đề, giả thuyết, setup, baseline, phương pháp, chỉ số chính, kết quả, một failure case |
| Code/notebook | Chạy được bằng lệnh ngắn hoặc chuỗi thao tác rõ ràng; ghi phiên bản dependencies |
| Bằng chứng | Ít nhất một bảng hoặc biểu đồ so sánh baseline với phương pháp |
| Thông tin tái lập | Seed/config, engine version, phần cứng/môi trường, workload chính xác |
| Pitch tối đa 4 slide | Pain → Approach → Evidence → Decision/Remaining risk |

### 4. Thang điểm và điều kiện loại kết quả

| Tiêu chí | Điểm | Ý nghĩa |
|---|---:|---|
| Chỉ số chính | 40 | Cải thiện metric trên kịch bản hợp lệ |
| Tính hợp lệ của thí nghiệm | 20 | Baseline công bằng, kiểm soát biến, tái lập, held-out khi khả thi |
| Prototype hoạt động | 15 | Code/mô phỏng chạy và sinh ra kết quả báo cáo |
| Chiều sâu nghiên cứu | 10 | Sử dụng paper/docs để hiểu và giải thích trade-off |
| Phân tích thất bại | 10 | Nêu giới hạn, trường hợp thất bại, rủi ro triển khai |
| Truyền đạt | 5 | Giải thích rõ trong 4 slide và trả lời chính xác |

Các giới hạn điểm: thiếu baseline thì phần metric tối đa 20/40; thiếu thí nghiệm/mô phỏng chạy được thì tổng điểm tối đa 60/100. Mất tính đúng đắn dữ liệu mà không phát hiện hoặc bịa số liệu làm kết quả vô hiệu, bất kể tốc độ.

### 5. Chín đề tài và chỉ số trọng tâm

| # | Đề tài, trang PDF | Bài toán và thí nghiệm tối thiểu | Baseline | Chỉ số chính |
|---|---|---|---|---|
| 1 | AI Coding Agent Safety, 4–5 | Agent làm việc hữu ích nhưng xử lý an toàn thao tác rủi ro. Ít nhất 20 prompt: 8 benign, 8 risky, 4 ambiguous; có retention, schema, DELETE/MERGE, nhầm bảng/môi trường | Agent có quyền ghi rộng, không policy/dry-run | Safety-Utility Score = `2SU/(S+U)`; S là tỷ lệ xử lý an toàn prompt risky/ambiguous, U là tỷ lệ hoàn thành hữu ích prompt benign |
| 2 | Smart Compaction, 6–7 | Quyết định COMPACT/SKIP trước khi biết kết quả. Ít nhất 3 trạng thái file; có truy vấn selective và full scan; đo thời gian/bytes rewrite | Compact khi file count vượt ngưỡng cố định | Net Time Saved = tổng thời gian truy vấn tiết kiệm, có tính số lần lặp workload, trừ thời gian compaction |
| 3 | Adaptive Data Layout, 8–9 | So sánh ít nhất 2 layout trên cùng dữ liệu; có 3 pha workload đổi filter; đo riêng chi phí rewrite | Giữ nguyên layout ban đầu | Weighted Query Cost Reduction = `1 - Σ(w_i T_ours_i)/Σ(w_i T_base_i)`; có thể dùng bytes scanned nếu đo đáng tin cậy |
| 4 | Autonomous Maintenance, 10–11 | Controller chọn ít nhất 3 thao tác bảo trì và NO-OP qua chuỗi trạng thái, trong ngân sách cố định | Chạy mọi thao tác theo lịch cố định | Tỷ lệ cửa sổ truy vấn đạt SLA, với chi phí bảo trì không vượt budget |
| 5 | Retention Policy Optimizer, 12–13 | Phân bổ retention cho ít nhất 3 profile; mô phỏng ít nhất 100 incident; công khai phân phối detection delay; có mất hạ tầng | Một retention chung cho mọi bảng | Recovery Coverage ở cùng storage budget; hoặc tối thiểu storage với coverage ≥95% |
| 6 | Metadata Scaling, 14–15 | Giữ nguyên dữ liệu và kết quả truy vấn, thử ít nhất 3 mức metadata/file count, benchmark ít nhất 5 lần mỗi mức | Không bảo trì metadata | Planning Speedup = `p95 planning baseline / p95 planning ours`; giải thích proxy nếu không đo riêng được planning |
| 7 | Concurrent Writers, 16–17 | Ít nhất 3 kiểu writer/access, có vùng giao nhau và không giao nhau; chạy lặp, kiểm tra bằng oracle độc lập | Writer đồng thời với retry mặc định | Successful commits/second với `LostUpdateCount=0`, `WrongFinalRows=0` |
| 8 | Point-in-Time Validator, 18–19 | Ít nhất 100 join case có ground truth clean/leaky; nhiều dạng leakage; có held-out | Chỉ loại khi feature timestamp > prediction timestamp | Leakage Recall với FPR ≤5% |
| 9 | Fair Lakehouse Benchmark, 20–21 | Ít nhất 2 format, ít nhất 4 loại workload; kiểm soát dữ liệu/tài nguyên, chạy lặp; chọn format từ development rồi kiểm tra holdout | Một query, một lần chạy, cấu hình mặc định | Recommendation Regret = `(Cost_chosen - min Cost)/min Cost` trên holdout; càng thấp càng tốt |

### 6. Quy trình 2 giờ được đề xuất trong PDF

| Thời gian | Công việc |
|---|---|
| 0–10 phút | Chọn đề tài, viết giả thuyết một câu, chốt metric |
| 10–30 phút | Đọc ít nhất một tài liệu chính thức và một paper/bài kỹ thuật khi có |
| 30–75 phút | Xây thí nghiệm nhỏ nhất có thể bác bỏ giả thuyết |
| 75–95 phút | Chạy baseline và phương pháp, lặp phép đo, ghi một failure/edge case |
| 95–110 phút | Làm README và 4 slide; chốt kết quả, tránh đổi metric cuối giờ |
| 110–120 phút | Nộp bài; nếu trình bày nằm trong 2 giờ thì điều chỉnh thời gian xây dựng |

Checklist cốt lõi ở trang 22: người khác chạy lại được, baseline và phương pháp dùng điều kiện tương đương, metric đúng định nghĩa, không tune trên holdout, có thất bại và mọi con số đến từ thí nghiệm/mô phỏng thực sự.

### 7. Nhóm tài liệu tham khảo của PDF

PDF liệt kê R1–R12: Delta Lake ACID/time travel/MERGE; Iceberg maintenance; Delta VACUUM; AutoComp; Smart Compaction; liquid clustering; predictive optimization; Flink maintenance; operation metrics; phân rã chức năng storage formats; Feast point-in-time joins; LHBench.

Với đề tài 5, các nguồn khởi đầu là **R1, R2, R3**, tập trung vào lịch sử bảng, snapshot expiration và dọn file. Danh mục này là nguồn được PDF gợi ý, không có nghĩa toàn bộ paper/link đã được kiểm chứng trong bản tóm tắt. Phần phân tích sau có đối chiếu tài liệu chính thức liên quan trực tiếp.

## II. Phân tích kỹ đề tài 5: Retention Policy Optimizer

### 1. Bài toán thực sự cần giải quyết

**Câu hỏi:** Với ngân sách lưu trữ có hạn, mỗi loại bảng cần giữ lịch sử bao lâu để khôi phục được nhiều sự cố nhất?

Retention là thời gian hoặc chính sách giữ các phiên bản/snapshot cùng những thành phần cần thiết để đọc lại chúng. TTL là thời hạn giữ; trong đề tài này, TTL khác nhau theo bảng hoặc nhóm bảng.

Giữ lịch sử ngắn giảm dung lượng nhưng có thể xóa phiên bản sạch trước khi phát hiện lỗi. Giữ quá dài cho mọi bảng làm ngân sách bị tiêu hao vào lịch sử ít hữu ích. Thách thức là phân bổ ngân sách theo nhu cầu thực tế.

Ba loại bảng có thể rất khác nhau:

- **Raw ingest:** lượng ghi lớn; nếu thật sự có nguồn độc lập còn giữ dữ liệu và có thể replay, một phần nhu cầu phục hồi có thể được đáp ứng ngoài lịch sử bảng. Không được mặc định khả năng replay luôn tồn tại.
- **Curated/business:** UPDATE/MERGE có thể làm sai dữ liệu đã công bố; thời gian phát hiện phụ thuộc quy trình đối soát.
- **Training dataset:** việc tái lập có thể diễn ra nhiều tuần sau; cần đọc đúng phiên bản đã dùng ở một lần huấn luyện.

Vì vậy, retention tối ưu phụ thuộc đồng thời **thời gian cần nhìn lại**, **chi phí lưu thêm lịch sử**, **tần suất sự cố** và **các ràng buộc bắt buộc**.

### 2. Các yêu cầu bắt buộc từ PDF

Theo trang 12–13, thí nghiệm phải có:

1. Ít nhất **3 table profile**, khác nhau về write/update rate và mức độ quan trọng.
2. Một phân phối **incident-detection delay** được tạo hoặc giả định, trình bày rõ.
3. **Storage budget cố định hoặc minimum recovery target**; không đồng thời tối ưu hai mục tiêu mà thiếu ràng buộc.
4. Ít nhất một tình huống **mất hạ tầng mà retention không giải quyết được**.
5. Baseline dùng **cùng một retention duration cho mọi bảng**.
6. Ít nhất **100 incident hoặc sự kiện tương tự lịch sử**, có detection delay khác nhau; kiểm tra phiên bản đích còn giữ được hay không.

Metric mặc định:

```text
RecoveryCoverage = recoverable_incidents / total_incidents
```

So sánh ở cùng ngân sách lưu trữ. Hướng thay thế được phép: giảm storage overhead với điều kiện coverage ≥95%. Nên chốt một hướng trước khi chạy test.

Các tiêu chí phụ: storage multiplier, average recoverable lookback, khả năng tái lập training run, policy violations, simulated RPO/RTO misses. Kết quả mạnh còn có đường Pareto giữa dung lượng và coverage, đồng thời giải thích được vì sao các bảng nhận TTL khác nhau.

### 3. Retention, rollback và backup khác nhau thế nào?

| Khái niệm | Chức năng | Giới hạn cần nêu |
|---|---|---|
| Retention lịch sử | Giữ khả năng tham chiếu/đọc lại trạng thái cũ | Chính sách trên giấy không đủ nếu file hoặc metadata đã mất |
| Time travel | Đọc bảng tại version/snapshot cũ | Cần các thành phần của phiên bản đó còn truy cập được |
| Rollback/restore | Phục hồi trạng thái hợp lệ trước lỗi logic | Không thể trông cậy vào file đã bị xóa vật lý |
| Backup/replication độc lập | Tạo đường phục hồi ngoài vị trí lưu trữ chính | Phải đánh giá phạm vi lỗi, tính độc lập và khả năng restore |

Ví dụ: MERGE sai hôm thứ Hai, phát hiện hôm thứ Sáu. Nếu trạng thái sạch trước MERGE còn đủ metadata và file, lịch sử có thể hỗ trợ phục hồi. Nếu toàn bộ storage chứa dữ liệu và lịch sử bị mất, tăng TTL từ 7 lên 90 ngày cũng không tạo ra bản sao phục hồi độc lập.

**Đối chiếu kỹ thuật:** Delta time travel cần cả log và data file của phiên bản. `delta.logRetentionDuration` và `delta.deletedFileRetentionDuration` điều khiển hai thành phần khác nhau. [Delta Lake: Data retention](https://docs.delta.io/delta-batch/#data-retention).

`VACUUM` dọn data file không còn được tham chiếu theo retention; log có cơ chế cleanup riêng. Tài liệu Delta khuyến nghị khoảng giữ an toàn ít nhất 7 ngày và dài hơn transaction chạy lâu nhất/stream lag dài nhất. [Delta Lake: Table utility commands](https://docs.delta.io/delta-utility/).

Với Iceberg, expire snapshot làm snapshot cũ không còn dùng cho time travel; file dữ liệu chỉ được dọn khi không còn snapshot cần chúng. Orphan cleanup là một thao tác riêng, có rủi ro với file của tác vụ ghi chưa hoàn tất. [Apache Iceberg: Maintenance](https://iceberg.apache.org/docs/latest/maintenance/).

**Hệ quả cho mô hình đề xuất:** Không đánh đồng TTL, độ tuổi file và lịch dọn file. Khi chuyển sang engine thật, cần kiểm tra semantics của phiên bản cụ thể và mọi cơ chế giữ tham chiếu lịch sử.

### 4. Định nghĩa đúng “cần giữ bao lâu”

Đặt:

- `t_bad`: lúc thao tác lỗi được commit.
- `t_target`: thời điểm phiên bản sạch cần phục hồi, thường trước `t_bad`.
- `t_detect`: lúc phát hiện sự cố.
- `t_restore`: lúc bắt đầu dùng phiên bản để phục hồi.
- `D = t_detect - t_bad`: detection delay.
- `A = t_bad - t_target`: khoảng cách từ phiên bản sạch đến commit lỗi.
- `L = t_restore - t_detect`: độ trễ phản ứng sau phát hiện.

Tuổi lịch sử thực sự cần tại thời điểm phục hồi là:

```text
H = t_restore - t_target = A + D + L
```

Mô hình đơn giản có thể giả định `A≈0`, `L=0` và dùng `D` làm proxy. Phải công khai giả định này. Trong mô hình nâng cao, dùng `H` tránh kết luận quá lạc quan khi snapshot thưa hoặc đội vận hành phản ứng chậm.

Với sự kiện `e` trên bảng `i`, bộ kiểm chứng xác định:

```text
recoverable(e, policy) =
    target_version_is_available
    AND all_required_files_are_available
    AND metadata_is_readable
    AND storage_infrastructure_is_available
```

Trong mô phỏng TTL lý tưởng không có pinning, ba điều kiện đầu có thể được xấp xỉ bằng `H_e <= r_i`. Điều kiện hạ tầng vẫn phải kiểm tra riêng. Đây là xấp xỉ phục vụ prototype, không phải bảo đảm phục hồi của mọi lakehouse.

### 5. Mô hình tối ưu hóa đề xuất

#### 5.1. Biến và dữ liệu đầu vào

| Ký hiệu | Ý nghĩa |
|---|---|
| `r_i` | Retention được chọn cho bảng/nhóm bảng i, tính bằng ngày |
| `c_i(r_i)` | Dung lượng lịch sử tăng thêm khi chọn retention đó |
| `B` | Tổng budget cho lịch sử tăng thêm |
| `F_i(r)` | Xác suất tuổi phiên bản cần phục hồi không vượt r |
| `p_i` | Tỷ trọng incident thuộc nhóm i, tổng bằng 1 |
| `r_min_i` | Retention tối thiểu theo yêu cầu đã xác định của nhóm i |

Mục tiêu đơn giản, khi chưa xét mất hạ tầng:

```text
maximize    Σ_i p_i * F_i(r_i)
subject to  Σ_i c_i(r_i) <= B
            r_i >= r_min_i
```

`F_i` nên được ước lượng từ development data hoặc một phân phối giả định công khai. Nếu thêm trọng số thiệt hại theo criticality, hàm mục tiêu sẽ khác tỷ lệ khôi phục không trọng số. Khi đó vẫn phải báo cáo RecoveryCoverage gốc; expected loss hoặc risk-weighted coverage là chỉ số bổ sung, trừ khi đã tuyên bố và biện minh một metric thay thế trước thử nghiệm.

Nếu một tỷ lệ sự cố là mất hạ tầng không có backup độc lập, coverage tổng có trần thấp hơn 100%. Chẳng hạn 8% sự kiện mất toàn bộ dữ liệu và lịch sử thì trần lý tưởng là 92% trong mô hình ấy. Đây là suy luận từ giả định; mục tiêu ≥95% sẽ không khả thi dù tăng TTL vô hạn.

#### 5.2. Chi phí lưu trữ không chỉ là lượng ghi mới

Một xấp xỉ cho prototype:

```text
c_i(r) = h_i * r
```

`h_i` là GB/ngày của **file lịch sử tăng thêm phải giữ**, không phải toàn bộ bytes ingest. Bảng append-only có thể tiếp tục dùng file cũ trong trạng thái hiện tại; giữ snapshot không nhất thiết tạo thêm một bản sao toàn bảng. UPDATE, DELETE, compaction và rewrite có thể tạo file cũ cần giữ, làm overhead khác hẳn append thuần.

Mô hình tốt hơn đếm file vật lý duy nhất:

```text
storage(policy, t) =
    sum(size(f) for unique files required by retained states at t)
    + required_metadata_bytes
```

Không cộng dung lượng từng snapshot độc lập vì nhiều snapshot dùng chung file. Chốt rõ budget là **history overhead**, **total live storage** hay **GB-days**. Không dùng cùng một giá trị số để thay thế các đại lượng có đơn vị khác nhau.

Nếu dùng overhead, tổng dung lượng là `current_data + history_overhead + metadata`. Phần current data phải giống nhau giữa các policy. Nếu dùng mô phỏng động, có thể ràng buộc `max_t storage(policy,t) <= B` hoặc dùng bình quân/GB-days, nhưng phải công bố trước vì kết luận có thể khác.

#### 5.3. Hai cách đặt bài toán hợp lệ

- **Hướng A:** Cố định budget B, tối đa RecoveryCoverage. Phù hợp nhất để bám metric mặc định của đề bài.
- **Hướng B:** Cố định coverage ≥95%, tìm storage nhỏ nhất. Phải kiểm tra tính khả thi, đặc biệt khi có mất hạ tầng hoặc yêu cầu bắt buộc.

Nếu tổng chi phí retention tối thiểu đã vượt B, trả về “không khả thi”; không âm thầm bỏ yêu cầu của một bảng để làm đẹp kết quả.

### 6. Giả thuyết nghiên cứu có thể kiểm chứng

**Giả thuyết chính đề xuất:** “Ở cùng ngân sách giữ lịch sử, retention riêng theo nhóm bảng, dựa trên phân phối thời gian cần phục hồi và chi phí lịch sử tăng thêm, đạt RecoveryCoverage cao hơn TTL chung.”

Một giả thuyết bổ sung: “Lợi ích giảm khi detection delay giữa các nhóm gần nhau hoặc khi phân phối ở holdout thay đổi mạnh.”

Giả thuyết có thể bị bác bỏ: policy riêng có thể bằng hoặc kém baseline trên holdout. Đây vẫn là kết quả có ý nghĩa nếu thí nghiệm công bằng và giải thích được nguyên nhân.

### 7. Thiết kế ba profile để mô phỏng

Các giá trị sau là **giả định đầu vào minh họa**, cần thay bằng dữ liệu thật hoặc dùng nguyên trạng và công khai trong config. Cả ba nhóm dùng cùng đơn vị ngày và GB.

| Profile | Đặc điểm | History overhead giả định | Detection delay D giả định | Criticality và yêu cầu bổ sung |
|---|---|---:|---|---|
| Raw ingest | Ghi lớn, update/rewrite thường xuyên trong mô hình này | 20 GB/ngày | 90% Uniform(0,2), 10% Uniform(2,7) | Trung bình; giả định retention tối thiểu 1 ngày trong mô phỏng trừu tượng |
| Curated/business | Khối lượng nhỏ hơn, lỗi logic phát hiện qua đối soát | 5 GB/ngày | 80% Uniform(0,7), 20% Uniform(7,30) | Cao; tối thiểu 7 ngày theo yêu cầu giả định |
| Training dataset | Update ít hơn, kiểm tra/tái lập muộn | 2 GB/ngày | 70% Uniform(7,30), 30% Uniform(30,60) | Cao; yêu cầu tái lập training được đánh giá riêng |

TTL 1 ngày ở bảng đầu chỉ là ứng viên của mô phỏng lý tưởng, **không phải cấu hình VACUUM được khuyến nghị**. Khi thử engine thật, thay grid bằng các giá trị đáp ứng điều kiện an toàn của engine và workload.

Giữ ít nhất 100 sự kiện tổng theo yêu cầu. Đề xuất 1.000 sự kiện để giảm dao động nếu thời gian cho phép. Công khai số incident mỗi nhóm: nếu chia đều thì metric đại diện cho mixture cân bằng, chưa chắc đại diện production. Criticality không tự động trở thành trọng số trong metric chính.

Thêm một loại sự cố mất hạ tầng với tỷ lệ đã chốt. Sự cố này làm mất cả file hiện tại và lịch sử trong phạm vi mô phỏng, không có bản sao độc lập. Giữ cùng các sự kiện đó cho mọi policy.

### 8. Baseline công bằng và thuật toán phù hợp

#### 8.1. Baseline: TTL chung tốt nhất trong budget

Mọi bảng dùng cùng `r`. Với chi phí tuyến tính và grid TTL:

```text
chọn r lớn nhất trong grid sao cho:
    r >= max_i(r_min_i)
    Σ_i h_i * r <= B
```

Vì coverage không giảm khi tăng TTL trong mô hình này, chọn TTL chung khả thi lớn nhất tránh baseline quá yếu. Có thể trình bày thêm policy “30 ngày cho tất cả” như thực tế thường gặp, nhưng nếu nó vượt budget thì không dùng nó làm đối thủ hợp lệ ở cùng B.

“Cùng ngân sách” nghĩa là cùng một trần chi phí và cùng cách đo. Với grid rời rạc, không cần mọi policy tiêu hết B; phải báo cáo chi phí thật, phần budget còn dư và bảo đảm baseline được chọn công bằng.

#### 8.2. Phương pháp chính: tìm kiếm trên grid

Với 3 profile, mỗi profile có 6 giá trị TTL ứng viên, chỉ có `6^3 = 216` tổ hợp. Có thể kiểm tra mọi tổ hợp, loại tổ hợp vi phạm budget/minimum retention, rồi chọn coverage cao nhất trên development.

Đây là phương pháp **chính xác trên grid và mô hình đã chọn**, không chứng minh tối ưu cho mọi TTL liên tục hay mọi engine. Dùng quy tắc xử lý hòa: ưu tiên chi phí thấp hơn, sau đó thứ tự TTL cố định để tái lập.

#### 8.3. Hướng mở rộng: lợi ích biên trên dung lượng

Với nhiều bảng, tăng TTL từng bước theo:

```text
priority_i = estimated_coverage_gain_i / extra_storage_i
```

Ý tưởng: đầu tư thêm lịch sử ở nơi mỗi GB giúp bảo vệ nhiều incident hơn. Tuy nhiên greedy không bảo đảm tối ưu với các bước rời rạc và lợi ích không đều. Khi mở rộng, có thể dùng dynamic programming hoặc multiple-choice knapsack; so sánh với exhaustive search trên bài toán nhỏ để kiểm tra chất lượng.

### 9. Ví dụ số để thấy cơ chế phân bổ

**Minh họa giả định, chưa chạy thí nghiệm:** dùng `h=(20,5,2)` GB/ngày và budget overhead `B=810 GB`.

TTL chung 30 ngày dùng:

```text
20*30 + 5*30 + 2*30 = 810 GB
```

Một vector TTL riêng `(14,60,90)` dùng:

```text
20*14 + 5*60 + 2*90 = 760 GB <= 810 GB
```

Vector riêng dành ít dung lượng hơn cho raw và giữ curated/training dài hơn. Với các phân phối D ở mục 7, giả định `A=L=0`, không mất hạ tầng và mỗi nhóm có cùng số incident:

- TTL chung bao phủ toàn bộ raw, toàn bộ curated, và 70% training theo phân phối lý tưởng.
- TTL riêng bao phủ toàn bộ ba nhóm trong mô hình giới hạn độ trễ này.
- Coverage kỳ vọng tương ứng là `(1+1+0,7)/3 = 90%` và `100%`.

Đây là **tính toán lý thuyết trên giả định**, không phải coverage quan sát từ mô phỏng. Vector này cũng chưa được khẳng định là nghiệm tối ưu. Nếu holdout có raw incident phát hiện sau 20 ngày, lợi thế có thể giảm vì raw chỉ được giữ 14 ngày.

### 10. Protocol thí nghiệm đề xuất

1. **Chốt metric, đơn vị budget và giả định.** Ví dụ chọn coverage tổng tại B cố định, dùng overhead tuyến tính; công bố grid, minimum TTL và xử lý boundary `H=r`.
2. **Sinh development và holdout riêng.** Dùng seed riêng; mỗi tập có ít nhất 100 sự kiện tổng. Incident có table_id, loại sự cố, target_age H và ground truth về mất hạ tầng.
3. **Thiết kế policy chỉ trên development.** Ước lượng phân phối, chọn TTL chung và vector TTL riêng; khóa cấu hình trước test.
4. **Chạy hai policy trên cùng holdout.** Mỗi incident được đánh giá bởi cả baseline và phương pháp để so sánh theo cặp.
5. **Dùng evaluator độc lập.** Optimizer không tự quyết định một incident “đã phục hồi” bằng điểm số của mình. Evaluator kiểm tra sự tồn tại trạng thái/file hoặc điều kiện mô phỏng đã chốt.
6. **Báo cáo kết quả chính và phân nhóm.** Tổng coverage, coverage mỗi profile, riêng lỗi logic, riêng mất hạ tầng, storage thật và budget violations.
7. **Lặp nhiều seed.** Ví dụ 10 seed; báo cáo trung bình, độ lệch chuẩn hoặc khoảng tin cậy của chênh lệch coverage theo cặp. Không coi nhiều incident trong một lần sinh là nhiều lần thử nghiệm độc lập nếu chúng có tương quan.
8. **Chạy một holdout dịch chuyển phân phối.** Ví dụ tăng tail delay của raw, tăng rewrite overhead hoặc đổi mixture incident. Không chỉnh lại policy sau khi thấy kết quả.
9. **Vẽ đường Pareto.** Quét vài budget đã định; mỗi budget khóa policy từ development và đánh giá trên holdout. Giữ B chính làm kết quả trọng tâm, tránh chọn budget có lợi sau thử nghiệm.

Chênh lệch nên báo cáo bằng **điểm phần trăm**: `100*(Coverage_ours-Coverage_base)`. Nếu báo cáo phần trăm cải thiện tương đối, phải dùng công thức riêng và nêu rõ mẫu số.

### 11. Kiến trúc prototype và pseudocode

```text
profiles + budget + assumptions
                 |
        development incidents
                 |
     baseline / retention optimizer
                 |
          locked policy vectors
                 |
holdout incidents -> independent evaluator -> metrics + failure cases
```

Pseudocode cho mô phỏng TTL đơn giản:

```python
# Chi phí và tuổi phiên bản dùng cùng đơn vị ngày.
# Chỉ dùng dev_events trong optimize; holdout không truyền vào optimizer.
def recoverable(event, ttl):
    if event.infrastructure_lost:
        return False
    return event.target_age_days <= ttl[event.table_id]

def coverage(events, ttl):
    assert len(events) > 0
    return sum(recoverable(e, ttl) for e in events) / len(events)

def optimize(dev_events, candidate_vectors, history_cost, budget, min_ttl):
    feasible = [
        v for v in candidate_vectors
        if all(v[i] >= min_ttl[i] for i in min_ttl)
        and history_cost(v) <= budget
    ]
    if not feasible:
        raise ValueError("Budget cannot satisfy mandatory retention")
    # Highest dev coverage; lower cost breaks ties; stable vector order last.
    return min(feasible, key=lambda v: (
        -coverage(dev_events, v), history_cost(v), tuple(v.values())
    ))
```

Đây là bản phác thảo phương pháp, chưa phải chương trình đã chạy. Khi dùng snapshot/file simulator, thay phép so sánh tuổi bằng kiểm tra metadata và tập file cần thiết sau cleanup; các cấu phần còn lại giữ nguyên.

### 12. Các kiểm tra có giá trị cho prototype

- Incident ngay trong/ngoài retention; boundary đúng bằng TTL; target version nằm trước lỗi.
- Mất toàn bộ hạ tầng luôn không recoverable bằng retention trong mô hình không backup.
- Policy vượt budget bị loại, kể cả khi coverage cao.
- Mọi vector đều vi phạm retention tối thiểu thì báo không khả thi.
- File dùng chung bởi nhiều snapshot chỉ được tính một lần.
- Optimizer chỉ nhận development data; holdout chỉ đi qua evaluator.
- Với mô hình lý tưởng đã chốt, tăng TTL của một bảng không làm coverage bảng đó giảm. Nếu khác, cần kiểm tra evaluator hoặc giả định về budget/cleanup.

Các kiểm tra này bảo vệ tính đúng đắn của metric; việc code chạy xong không đủ chứng minh mô hình đánh giá đúng.

### 13. Chỉ số và bảng kết quả cần có

| Chỉ số | Cách tính/diễn giải |
|---|---|
| RecoveryCoverage chính | Recoverable/total trên cùng holdout và cùng budget; mẫu số gồm loại sự kiện nào phải khai báo |
| Coverage theo profile | Tránh che khuất việc một nhóm bị giảm bảo vệ |
| Logical-error coverage | Chỉ lỗi logic; chỉ số phụ nếu metric chính dùng mọi incident |
| Infrastructure-loss coverage | Cho thấy giới hạn của retention |
| History overhead | GB tăng thêm hoặc GB-days theo định nghĩa đã chọn |
| Storage multiplier | Total retained bytes/current logical-data bytes, tại cùng thời điểm |
| Training reproducibility coverage | Training replay request còn đọc được đúng snapshot/tổng replay request; không mặc định bằng incident coverage |
| Policy violations | Số vi phạm minimum TTL, budget hoặc yêu cầu pinning đã mô hình hóa |
| RPO/RTO misses | Chỉ báo cáo khi đã mô hình hóa điểm phục hồi và thời gian khôi phục; coverage không tự suy ra RTO |

Mẫu bảng để điền **sau khi thực thi**, không điền số giả:

| Policy | TTL raw/curated/training | Budget | Chi phí thực | Coverage tổng | Raw | Curated | Training | Vi phạm |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TTL chung | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy |
| TTL tối ưu theo profile | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy |

Đường Pareto đặt chi phí trên trục X, coverage trên trục Y. Một policy bị chi phối nếu policy khác có coverage không thấp hơn và chi phí không cao hơn, với ít nhất một mặt tốt hơn.

### 14. Failure case và giới hạn phải phân tích

| Tình huống | Vì sao có thể thất bại | Cách kiểm tra/giải thích |
|---|---|---|
| Phát hiện lỗi muộn hơn development | TTL được học từ phân phối cũ quá ngắn | Holdout có tail delay dài hơn; báo coverage theo nhóm |
| Rewrite/compaction tăng | Chi phí lịch sử mỗi ngày cao hơn ước lượng | Tăng `h_i` hoặc dùng trace file thật; kiểm tra budget |
| Mất object storage và lịch sử cùng lúc | Không còn dữ liệu để time travel | Incident hạ tầng riêng, cùng failure domain |
| Metadata còn nhưng data file đã dọn | Có tên version nhưng không đọc được trạng thái | Evaluator kiểm tra file, không chỉ version ID |
| Nhiều bảng cần phục hồi đồng bộ | TTL riêng từng bảng chưa bảo đảm một thời điểm nhất quán chung | Kịch bản phục hồi pipeline nhiều bảng; nêu giới hạn nếu chưa làm |
| Training cần tái lập sau thời gian rất dài | Incident delay chưa đại diện cho nhu cầu replay | Sinh replay requests riêng hoặc thêm ràng buộc giữ snapshot |
| Nhóm ít incident nhưng rất quan trọng | Metric đếm sự kiện có thể bỏ qua hậu quả lớn | Minimum constraints và expected-loss metric phụ |
| Các nhóm gần giống nhau | Không có nhiều lợi ích từ phân bổ TTL riêng | Thử delay/cost đồng nhất; chấp nhận kết quả bằng baseline |

Retained training snapshot chỉ bảo vệ phần dữ liệu đã mô hình hóa. Tái lập đầy đủ còn phụ thuộc code, cấu hình, feature logic và các đầu vào bên ngoài. Không nên tuyên bố “tái lập training hoàn toàn” chỉ từ coverage lịch sử bảng.

### 15. Phạm vi khả thi trong 2 giờ

**Đề xuất triển khai:** mô phỏng Python với 3 profile, grid search, một budget chính, development/holdout riêng và một failure scenario. Đề bài cho phép simulation, nên không cần dựng Spark/catalog/object storage nếu chúng không giúp kiểm chứng giả thuyết trong thời gian ngắn.

| Thời gian | Công việc cho đề tài 5 |
|---|---|
| 0–10 phút | Chốt giả thuyết, định nghĩa recovery, chọn budget/đơn vị và baseline |
| 10–30 phút | Đọc retention/cleanup docs, chọn phân phối delay, công khai giả định |
| 30–75 phút | Viết generator, cost model, evaluator, TTL baseline và grid search |
| 75–95 phút | Chạy paired comparison, nhiều seed và một scenario dịch chuyển/mất hạ tầng |
| 95–110 phút | Xuất bảng/Pareto, README và nội dung 4 slide |
| 110–120 phút | Kiểm tra chạy lại, khóa kết quả, nộp |

Nếu có thời gian ngoài sprint, ưu tiên bổ sung snapshot/file simulator trước khi chuyển sang thuật toán học máy. Điều này giúp kiểm chứng hai giả định khó nhất: chi phí file lịch sử thực tế và tính khả dụng của phiên bản sau cleanup.

### 16. Điểm mới và chiều sâu nghiên cứu

Đề tài có mức khó thấp–trung bình theo PDF, thuận lợi cho prototype nhanh. Tuy nhiên, phần giá trị nằm ở **cách mô hình hóa và kiểm chứng**, không chỉ ở một công thức chọn TTL.

Một bài tốt cần chứng minh: nguồn tiết kiệm dung lượng đến từ đâu, ngân sách được tái phân bổ cho incident nào, tại sao lợi ích giữ được trên holdout và điều kiện nào làm phương pháp thất bại. Grid search là công cụ giải bài toán; nó tự thân chưa phải đóng góp nghiên cứu mới.

Các hướng mở rộng có ý nghĩa:

- Retention theo distribution tail/quantile thay vì chỉ delay trung bình.
- Kết hợp TTL với giữ một số snapshot quan trọng của training run, có tính đủ chi phí giữ thêm.
- Robust optimization khi ước lượng detection delay còn ít dữ liệu.
- Cost model theo file lineage thay vì GB/ngày tuyến tính.
- Retention đồng bộ theo nhóm bảng phụ thuộc nhau để phục hồi pipeline nhất quán.

Nếu muốn phát triển thành nghiên cứu dài hơn, cần khảo sát thêm literature và so sánh các phương pháp tương ứng; bản phân tích này chưa khẳng định tính mới so với toàn bộ công trình hiện có.

### 17. Gợi ý nội dung 4 slide và câu hỏi bảo vệ

**Slide 1:** Một TTL chung gây trade-off gì; giả thuyết cùng budget, coverage cao hơn nhờ phân bổ theo profile.

**Slide 2:** Ba profile, phân phối delay, cost model, baseline, grid search, split development/holdout.

**Slide 3:** Kết quả đo thực: coverage tổng/theo bảng, chi phí, chênh lệch qua nhiều seed, đường Pareto.

**Slide 4:** Failure case, giới hạn time travel với mất hạ tầng, giả định còn cần kiểm tra trước triển khai.

| Câu hỏi có thể gặp | Điểm cần trả lời |
|---|---|
| Vì sao không giữ 30 ngày cho mọi bảng? | Chi phí và độ trễ phục hồi khác nhau; so sánh phải cùng budget |
| Baseline có bị làm yếu không? | Chọn TTL chung lớn nhất khả thi theo cùng grid/minimum constraints |
| Có dùng test để chọn TTL không? | Chỉ development đi vào optimizer; khóa policy trước holdout |
| Có phải backup optimizer không? | Phạm vi là lịch sử bảng; mất hạ tầng được mô hình hóa như giới hạn |
| Tại sao training giữ dài hơn raw? | Cần replay muộn hơn trong giả định, chi phí lịch sử/GB có thể thấp hơn; kiểm chứng trên profile thực |
| Nếu coverage không tăng thì sao? | Báo kết quả thật, phân tích phân phối/chi phí hoặc shift; không đổi metric sau test |
| Có thể đạt 95% luôn không? | Không, phải kiểm tra trần coverage và tính khả thi của budget |

### 18. Kết luận đánh giá đề tài

Retention Policy Optimizer phù hợp nếu muốn một prototype gọn nhưng có lập luận định lượng rõ. Phương án khởi đầu hợp lý là **tối đa RecoveryCoverage dưới một budget cố định**, dùng TTL chung làm baseline và grid search cho TTL từng nhóm.

Ba điểm quyết định chất lượng bài làm là: tính đúng chi phí lịch sử tăng thêm, đánh giá khả dụng của phiên bản thực sự cần phục hồi, và kiểm tra trên holdout có failure case. Lợi ích của phương pháp phải đến từ phân bổ ngân sách tốt hơn, không từ chi nhiều hơn hay loại các sự cố khó khỏi mẫu số.

## III. Nguồn và phạm vi kiểm chứng

1. **PDF do người dùng cung cấp:** trang 1–3 cho mục tiêu, nộp bài và chấm điểm; trang 4–21 cho 9 đề tài; trang 12–13 cho Retention Policy Optimizer; trang 22 cho workflow/checklist; trang 23 cho R1–R12.
2. [Delta Lake: Table batch reads and writes, Data retention](https://docs.delta.io/delta-batch/#data-retention). Đối chiếu ngày 04/10/2026, phục vụ phân biệt retention của log và data file.
3. [Delta Lake: Table utility commands](https://docs.delta.io/delta-utility/). Đối chiếu ngày 04/10/2026, phục vụ semantics và điều kiện an toàn của VACUUM.
4. [Apache Iceberg: Maintenance](https://iceberg.apache.org/docs/latest/maintenance/). Đối chiếu ngày 04/10/2026, phục vụ snapshot expiration và orphan cleanup. `latest` có thể thay đổi; thí nghiệm cần ghi phiên bản thực tế.

Các mô hình toán, profile, thuật toán, protocol và ví dụ số ở Phần II là **đề xuất phân tích**, không phải yêu cầu nguyên văn của PDF hoặc kết quả thực nghiệm. Chưa xây/chạy prototype lakehouse hay simulation trong phạm vi yêu cầu tạo bản tóm tắt và phân tích này.

## IV. Phương án triển khai cho nhóm 4 người

### 1. Thành viên và phân công đề xuất

Nhóm gồm **Nguyễn Đình Phúc, Đoàn Tuấn Long, Nguyễn Việt Thành và Đinh Ngọc Đức**. Phân công dưới đây dựa trên các đầu việc của đề tài, chưa dựa trên thế mạnh cá nhân; nhóm có thể đổi người phụ trách mà giữ nguyên trách nhiệm và đầu ra.

| Thành viên | Vai trò đề xuất | Công việc chính | Đầu ra chịu trách nhiệm |
|---|---|---|---|
| Nguyễn Đình Phúc | Mô hình bài toán và nghiên cứu | Đọc docs; chốt giả thuyết, metric, đơn vị budget, minimum TTL; giải thích retention/time travel/backup; ghi giả định và giới hạn; soạn prompt và kiểm tra nhận xét LLM trong report | `README.md`, phần giả định của `config.json`, prompt nhận xét LLM, nội dung slide 1 |
| Đoàn Tuấn Long | Dữ liệu và môi trường mô phỏng | Xây 3 profile; sinh development/holdout với seed riêng; mô hình hóa detection delay và tuổi phiên bản đích; thêm mất hạ tầng và dịch chuyển phân phối | `generator.py`, dữ liệu sự kiện có schema thống nhất, mô tả scenario |
| Nguyễn Việt Thành | Baseline và thuật toán tối ưu | Viết cost model; chọn TTL chung khả thi lớn nhất; tìm vector TTL theo grid trên development; xuất policy đã khóa | `cost_model.py`, `policies.py`, policy baseline/phương pháp, nội dung slide 2 |
| Đinh Ngọc Đức | Đánh giá và report | Viết evaluator độc lập; kiểm tra budget/correctness; so sánh theo cặp trên holdout, chạy nhiều seed; tự động xuất report HTML, bảng, Pareto và tích hợp nhận xét LLM | `evaluate.py`, bộ sinh report HTML, `results.csv`, dữ liệu kết quả JSON, report cho từng lần eval, nội dung slide 3–4 |

Tên file là cấu trúc đề xuất cho bước triển khai tiếp theo; các file code trên chưa được tạo. Cả nhóm cùng kiểm tra kết quả, thống nhất kết luận và hoàn thiện pitch. Người làm đánh giá không chỉnh thuật toán theo kết quả holdout.

### 2. Thống nhất giao diện trước khi viết code

Trong 10 phút đầu, cả nhóm chốt các quy ước sau để các phần có thể ghép được:

| Thành phần | Quy ước đề xuất |
|---|---|
| Profile | `table_id`, `history_gb_per_day`, `min_retention_days`, phân phối delay |
| Incident | `incident_id`, `table_id`, `scenario`, `target_age_days`, `infrastructure_lost` |
| Policy | Ánh xạ `table_id -> retention_days`; baseline có cùng giá trị cho mọi bảng |
| Budget | History overhead, đơn vị GB, cost model tuyến tính cho prototype đầu tiên |
| Recovery | Không mất hạ tầng và `target_age_days <= retention_days`; công khai đây là mô hình lý tưởng |
| Split | Development và holdout được sinh riêng; optimizer chỉ nhận development |
| So sánh | Hai policy dùng đúng cùng incident trong mỗi lần đánh giá, cùng budget và cost model |
| Kết quả | Coverage tổng/theo profile, actual cost, budget violations, chênh lệch coverage theo điểm phần trăm |
| Report mỗi lần eval | Sinh HTML từ kết quả của chính lần chạy, kèm vài câu nhận xét LLM; lưu theo run ID để truy xuất lại |

Nguyễn Việt Thành và Đinh Ngọc Đức thống nhất giao diện cost/evaluation, nhưng Đức kiểm tra logic phục hồi độc lập. Long cung cấp một bộ dữ liệu nhỏ để ghép thử trước khi sinh toàn bộ thí nghiệm; bộ thử giao diện này không thay thế holdout cuối cùng.

### 3. Lịch làm việc song song trong sprint 2 giờ

| Mốc | Phúc | Long | Thành | Đức |
|---|---|---|---|---|
| 0–10 phút | Cùng nhóm chốt giả thuyết, metric và schema | Cùng nhóm chốt profile/incident | Cùng nhóm chốt baseline/grid | Cùng nhóm chốt protocol và evaluator |
| 10–30 phút | Đọc docs, ghi giả định | Thiết kế phân phối và generator | Thiết kế cost model, baseline, grid search | Thiết kế evaluator và kiểm tra edge case |
| 30–60 phút | Viết README nháp, rà yêu cầu PDF | Hoàn thiện generator và scenario | Hoàn thiện baseline/optimizer | Hoàn thiện evaluator và xuất kết quả |
| 60–75 phút | Kiểm tra mô hình khớp mô tả | Kiểm tra schema, seed và tách tập | Ghép optimizer với development | Ghép evaluator, chạy thử toàn pipeline |
| 75–95 phút | Soạn prompt LLM, kiểm tra nhận xét và giới hạn | Chạy/cung cấp scenario failure đã chốt | Khóa policy, hỗ trợ kiểm tra budget | Chạy holdout, nhiều seed, xuất report HTML và tích hợp LLM |
| 95–110 phút | Hoàn thiện README, slide 1; rà nhận xét LLM | Kiểm tra mô tả dataset/scenario | Hoàn thiện slide 2 | Kiểm tra report HTML, bảng/biểu đồ, slide 3–4 |
| 110–120 phút | Cùng nhóm kiểm tra bộ nộp và kết luận | Kiểm tra tái lập dữ liệu | Kiểm tra policy/cost | Chạy lại từ lệnh trong README |

Không chờ nghiên cứu tài liệu hoàn tất mới bắt đầu code: nhóm dùng giả định đã chốt để làm song song, cập nhật khi tìm thấy vấn đề kỹ thuật. Nếu thay đổi mô hình ảnh hưởng kết quả, cập nhật config và chạy lại toàn bộ so sánh cần thiết.

### 4. Kiểm tra chéo và điều kiện hoàn thành

- **Phúc kiểm tra phần của Thành:** hàm mục tiêu, baseline và ràng buộc có đúng với giả thuyết/README không.
- **Thành kiểm tra phần của Long:** phân phối, đơn vị thời gian, schema và cost input có nhất quán không.
- **Long kiểm tra phần của Đức:** evaluator xử lý đúng các incident biết trước, nhất là boundary và mất hạ tầng.
- **Đức kiểm tra phần của Phúc:** mọi con số trong báo cáo có truy ra kết quả chạy thực, mọi giả định có được ghi rõ không.

Nhóm hoàn thành khi có: 3 profile; ít nhất 100 incident ở thí nghiệm đánh giá; phân phối delay rõ ràng; baseline công bằng; một budget cố định; policy khóa trước holdout; một failure case; bảng hoặc biểu đồ từ lần chạy thật; **report HTML tự động cho mỗi lần eval, kèm vài câu nhận xét LLM**; README chạy lại được; pitch tối đa 4 slide.

Khi trình bày, Phúc giải thích vấn đề và giả thuyết; Long trả lời về dữ liệu và scenario; Thành giải thích phương pháp; Đức trình bày bằng chứng và thất bại. Có thể chọn một người trình bày chính, còn ba người phụ trách Q&A theo phần việc.

## V. Yêu cầu bổ sung từ giảng viên: Report HTML và nhận xét LLM

### 1. Yêu cầu được nhóm cung cấp

Theo thông tin người dùng bổ sung về hướng dẫn của thầy: **mỗi lần chạy evaluation cần có một report HTML, thêm vài câu nhận xét của LLM**. Đây là yêu cầu bổ sung ngoài nội dung PDF đã tóm tắt. Trong kế hoạch của nhóm, yêu cầu này được đưa vào đầu ra và checklist hoàn thành.

Các chi tiết sau là đề xuất cụ thể hóa để triển khai; thầy chưa được mô tả là đã quy định chính xác bố cục, số câu, model hoặc cách lưu file.

### 2. Luồng chạy đề xuất

```text
Chạy eval
   -> Tính và lưu kết quả thực tế (JSON/CSV)
   -> Gửi bản tóm tắt kết quả cho LLM
   -> Nhận 3–5 câu nhận xét bằng tiếng Việt
   -> Sinh report HTML chứa kết quả và nhận xét
```

Mỗi lần gọi lệnh eval sinh một report tổng hợp cho lần chạy đó, kể cả khi lần chạy gồm nhiều seed/scenario. Nếu eval không hợp lệ hoặc lỗi, report ghi rõ trạng thái và phần kết quả còn thiếu. Report là file HTML có thể mở bằng trình duyệt; phạm vi này chưa yêu cầu xây website hoặc triển khai hosting.

### 3. Nội dung tối thiểu của report

| Phần | Nội dung |
|---|---|
| Thông tin lần chạy | Run ID, thời điểm chạy, trạng thái, seed, scenario, config và phiên bản môi trường |
| Thiết lập thí nghiệm | Ba profile, budget và đơn vị, số incident, giả định phục hồi, TTL baseline và TTL tối ưu |
| Kết quả chính | Coverage baseline/phương pháp, chênh lệch theo điểm phần trăm, chi phí thực, budget violations |
| Kết quả theo nhóm | Coverage raw/curated/training; lỗi logic và mất hạ tầng khi có |
| Bằng chứng trực quan | Bảng so sánh và biểu đồ phù hợp; Pareto khi lần chạy có quét budget |
| Nhận xét LLM | 3–5 câu về kết quả, trade-off và giới hạn, dựa trên dữ liệu của lần chạy |
| Tái lập | Lệnh chạy, liên kết đến config và dữ liệu kết quả; failure case đã quan sát |

Đề xuất lưu từng lần vào `reports/<run_id>/report.html`, cùng `metrics.json`, `results.csv` và `llm_commentary.json`. Có thể thêm `reports/latest.html` để mở nhanh bản mới nhất; vẫn giữ report cũ để đối chiếu. Biểu đồ nên được nhúng vào HTML để dễ gửi và mở lại.

### 4. Quy tắc cho nhận xét LLM

LLM nhận số liệu đã tính bởi evaluator: coverage, cost, TTL, số incident, seed/scenario, violations, failure case và giới hạn mô hình. **Evaluator tính metric và quyết định tính hợp lệ**; LLM chỉ diễn giải kết quả.

Nhận xét cần dùng đúng số liệu, nêu rõ phương pháp cải thiện/giảm/không đổi, và đề cập ít nhất một trade-off hoặc giới hạn có bằng chứng. Nếu dữ liệu chưa đủ để giải thích nguyên nhân, LLM ghi đó là giả thuyết cần kiểm chứng. Không suy diễn kết quả của mô phỏng thành bảo đảm triển khai production.

Prompt đề xuất:

```text
Bạn đang nhận kết quả của một lần evaluation Retention Policy Optimizer.
Viết 3–5 câu nhận xét bằng tiếng Việt chỉ dựa trên JSON được cung cấp.
Nêu so sánh coverage và chi phí giữa baseline với phương pháp;
dùng điểm phần trăm khi nói về chênh lệch coverage.
Nêu một trade-off hoặc giới hạn được dữ liệu/giả định hỗ trợ.
Nếu có budget violation hoặc run không hợp lệ, nói rõ trước kết luận hiệu quả.
Không bịa số liệu, không khẳng định nguyên nhân khi chưa có bằng chứng,
không dùng nhận xét của bạn để thay đổi metric, policy hoặc kết quả eval.
```

Lưu model, prompt, phản hồi và trạng thái lời gọi cùng run ID để truy xuất. Nếu LLM lỗi hoặc chưa được cấu hình, report vẫn được xuất và ghi rõ “Chưa có nhận xét LLM” cùng lý do; không chèn nhận xét giả. Nhóm cần xử lý lỗi và tạo lại nhận xét để hoàn tất yêu cầu bổ sung.

### 5. Phân công và tiêu chí nghiệm thu

- **Đức:** dựng template HTML, bộ sinh report, tích hợp lời gọi LLM và lưu đầu ra mỗi lần eval.
- **Phúc:** soạn prompt, kiểm tra nhận xét có đúng số liệu và giới hạn nghiên cứu.
- **Thành:** cung cấp TTL, cost, budget và metadata phương pháp theo schema kết quả thống nhất.
- **Long:** cung cấp profile, seed, scenario và số incident để report giải thích được thí nghiệm.

Nghiệm thu khi chạy eval tạo được report HTML mở được, mọi số liệu trong report khớp JSON/CSV, nhận xét LLM bám đúng lần chạy, và hai lần eval có run ID riêng để không ghi đè bằng chứng. README phải chỉ rõ lệnh chạy eval, vị trí report, cấu hình LLM và cách nhận biết lời gọi LLM thất bại.

Phần này cập nhật yêu cầu và kế hoạch; chưa triển khai hoặc chạy bộ sinh HTML/LLM.
