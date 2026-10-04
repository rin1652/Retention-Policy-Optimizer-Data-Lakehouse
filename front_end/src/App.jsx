import React, { useState, useEffect } from 'react';
import './App.css';

const mockData = {
  run_id: "20261004T174719-daa6825e-a234c96a",
  budget_gb: 810,
  status: "valid",
  policies: {
    "baseline-S0_main-dev1001-B810": {
      kind: "baseline_uniform",
      ttl_days: { raw_ingest: 30, curated_business: 30, training_dataset: 30 },
      cost_gb: 810,
      coverage_total: 0.812,
      coverage_logical_only: 0.885,
      min_ttl_violations: 0,
      budget_violations: 0,
      recoverable: 730,
      total: 900
    },
    "optimized-S0_main-dev1001-B810": {
      kind: "optimized_per_profile",
      ttl_days: { raw_ingest: 7, curated_business: 30, training_dataset: 60 },
      cost_gb: 410, // Giả sử cost tối ưu thấp hơn hoặc bằng
      coverage_total: 0.945,
      coverage_logical_only: 0.991,
      min_ttl_violations: 0,
      budget_violations: 0,
      recoverable: 850,
      total: 900
    }
  },
  llm_commentary: {
    status: "success",
    model: "DeepSeek-V4-Flash",
    response: "Chính sách tối ưu đã đạt hiệu quả vượt trội so với baseline. Thay vì áp dụng đồng loạt 30 ngày (Baseline), việc giảm TTL của raw_ingest xuống 7 ngày và tăng training_dataset lên 60 ngày giúp tăng Recovery Coverage từ 81.2% lên 94.5% mà vẫn tuân thủ ngân sách 810GB. Các sự cố có độ trễ lớn trên bảng training đã được khôi phục thành công (do giữ lịch sử tới 60 ngày). Điều này chứng minh sự ưu việt của phương pháp tối ưu phân mảnh (per-profile) so với cách tiếp cận One-size-fits-all."
  },
  paired: {
    delta_pp: {
      "Optimized vs Baseline": 13.3
    }
  }
};

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Giả lập fetch data
    setTimeout(() => setData(mockData), 500);
  }, []);

  if (!data) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#fff' }}>
        <h2>Đang tải dữ liệu mô phỏng...</h2>
      </div>
    );
  }

  const baseline = Object.values(data.policies).find(p => p.kind === 'baseline_uniform');
  const optimized = Object.values(data.policies).find(p => p.kind === 'optimized_per_profile');

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1 className="title">Retention Policy Optimizer</h1>
        <p className="subtitle">Báo cáo Đánh giá Chính sách Data Lakehouse (Run ID: {data.run_id})</p>
      </header>

      <section className="metrics-grid">
        <div className="card" style={{ animationDelay: '0.1s' }}>
          <div className="card-title">Storage Budget</div>
          <div className="metric-value">
            {data.budget_gb} <span className="metric-unit">GB</span>
          </div>
        </div>
        <div className="card" style={{ animationDelay: '0.2s' }}>
          <div className="card-title">Baseline Coverage</div>
          <div className="metric-value" style={{ color: '#94a3b8' }}>
            {(baseline.coverage_total * 100).toFixed(1)} <span className="metric-unit">%</span>
          </div>
        </div>
        <div className="card" style={{ animationDelay: '0.3s', borderColor: 'var(--success-color)' }}>
          <div className="card-title" style={{ color: 'var(--success-color)' }}>Optimized Coverage</div>
          <div className="metric-value">
            {(optimized.coverage_total * 100).toFixed(1)} <span className="metric-unit">%</span>
          </div>
        </div>
        <div className="card" style={{ animationDelay: '0.4s' }}>
          <div className="card-title">Độ chênh lệch (Delta)</div>
          <div className="metric-value" style={{ color: 'var(--primary-color)' }}>
            +{data.paired.delta_pp["Optimized vs Baseline"].toFixed(1)} <span className="metric-unit">điểm %</span>
          </div>
        </div>
      </section>

      <section className="llm-commentary" style={{ animationDelay: '0.5s' }}>
        <div className="llm-text">
          {data.llm_commentary.response}
        </div>
      </section>

      <section className="policy-comparison" style={{ animationDelay: '0.6s' }}>
        <h2 style={{ marginBottom: '20px' }}>So sánh Chi tiết Cấu hình</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Chính sách</th>
                <th>Raw Ingest (TTL)</th>
                <th>Curated (TTL)</th>
                <th>Training (TTL)</th>
                <th>Chi phí (GB)</th>
                <th>Logic Coverage</th>
                <th>Khôi phục</th>
                <th>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Baseline</strong><br/><small style={{color:'var(--text-muted)'}}>Uniform TTL</small></td>
                <td><div className="ttl-box-simple">30 ngày</div></td>
                <td><div className="ttl-box-simple">30 ngày</div></td>
                <td><div className="ttl-box-simple">30 ngày</div></td>
                <td>{baseline.cost_gb}</td>
                <td>{(baseline.coverage_logical_only * 100).toFixed(1)}%</td>
                <td>{baseline.recoverable} / {baseline.total}</td>
                <td><span className="badge badge-warning">Cơ bản</span></td>
              </tr>
              <tr>
                <td><strong>Optimized</strong><br/><small style={{color:'var(--text-muted)'}}>Per-profile</small></td>
                <td><div className="ttl-box-simple highlight-down">7 ngày</div></td>
                <td><div className="ttl-box-simple">30 ngày</div></td>
                <td><div className="ttl-box-simple highlight-up">60 ngày</div></td>
                <td><strong style={{color: 'var(--success-color)'}}>{optimized.cost_gb}</strong></td>
                <td><strong style={{color: 'var(--success-color)'}}>{(optimized.coverage_logical_only * 100).toFixed(1)}%</strong></td>
                <td><strong style={{color: 'var(--success-color)'}}>{optimized.recoverable}</strong> / {optimized.total}</td>
                <td><span className="badge badge-success">Tối ưu</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="benchmark-section" style={{ animationDelay: '0.65s', marginTop: '50px' }}>
        <h2 style={{ marginBottom: '20px' }}>Benchmarks & Thông số Mô phỏng</h2>
        <div className="metrics-grid">
          <div className="card benchmark-card">
            <h3>Mô hình Chi phí (Cost Model)</h3>
            <p style={{fontSize: '1.1rem', fontFamily: 'monospace'}}>
              <strong>Công thức:</strong> Cost = Σ (History_GB/ngày × TTL_days)
            </p>
            <ul>
              <li><span className="badge">raw_ingest</span>: 20 GB/ngày</li>
              <li><span className="badge">curated_business</span>: 5 GB/ngày</li>
              <li><span className="badge">training_dataset</span>: 2 GB/ngày</li>
            </ul>
            <p className="text-muted"><small>Budget tối đa cho phép: <strong>810 GB</strong></small></p>
          </div>

          <div className="card benchmark-card">
            <h3>Giả lập Sự cố (Incidents)</h3>
            <p><strong>Quy mô:</strong> 900 sự cố phân bổ đều trên 3 bảng.</p>
            <ul>
              <li><strong>Raw Ingest:</strong> Lỗi dễ phát hiện, delay chỉ từ 0-7 ngày.</li>
              <li><strong>Curated / Training:</strong> Lỗi ẩn sâu, delay phát hiện lên tới 30-60 ngày.</li>
              <li><strong>Infra Loss:</strong> Tỷ lệ mất trắng hạ tầng (Bucket deletion) được mô phỏng ở mức 8%.</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="criteria-section" style={{ animationDelay: '0.7s', marginTop: '50px' }}>
        <h2 style={{ marginBottom: '20px' }}>Tiêu chí Chấm điểm & Ràng buộc TTL</h2>
        <div className="criteria-grid">
          <div className="criteria-card">
            <h3>Ràng buộc Kỹ thuật</h3>
            <ul>
              <li><strong>Hợp lệ (Validity):</strong> Target Age (H) phải ≤ TTL.</li>
              <li><strong>Storage Budget:</strong> Tổng chi phí History không được vượt quá 810GB.</li>
              <li><strong>Mất hạ tầng (Infra Loss):</strong> Không thể khôi phục (dù H ≤ TTL).</li>
            </ul>
          </div>
          <div className="criteria-card">
            <h3>Cơ cấu Chấm điểm</h3>
            <ul>
              <li><strong>Metric Chính (Coverage):</strong> 40đ <em>(Không có baseline cap 20đ)</em></li>
              <li><strong>Tính Hợp lệ Thí nghiệm:</strong> 20đ</li>
              <li><strong>Prototype Chạy được:</strong> 15đ <em>(Lỗi/Crash cap tổng 60đ)</em></li>
              <li><strong>Nghiên cứu & Phân tích lỗi:</strong> 20đ</li>
              <li><strong>Trình bày (Pitching):</strong> 5đ</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
