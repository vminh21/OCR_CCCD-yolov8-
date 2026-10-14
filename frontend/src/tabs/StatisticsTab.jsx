// frontend/src/tabs/StatisticsTab.jsx
import React, { useState, useEffect } from 'react';
import { apiGetStatistics, apiGetCorrections } from '../services/api';

export default function StatisticsTab({ showToast }) {
  const [stats, setStats] = useState(null);
  const [corrections, setCorrections] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStatsAndCorrections = async () => {
    setLoading(true);
    try {
      const [resStat, resCorr] = await Promise.all([
        apiGetStatistics(),
        apiGetCorrections(),
      ]);

      if (resStat.ok) {
        const dataStat = await resStat.json();
        setStats(dataStat);
      }
      if (resCorr.ok) {
        const dataCorr = await resCorr.json();
        setCorrections(dataCorr || []);
      }
    } catch (err) {
      showToast('❌ Lỗi tải thống kê: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatsAndCorrections();
  }, []);

  return (
    <div>
      {/* 4 STAT CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        {/* CARD 1: TỔNG SỐ LẦN QUÉT */}
        <div className="card" style={{ padding: '20px' }}>
          <div className="stat-card-header">
            <span className="stat-label">Tổng Số Lượt Quét</span>
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <rect x="2" y="3" width="20" height="14" rx="2" />
                <line x1="8" y1="21" x2="16" y2="21" />
                <line x1="12" y1="17" x2="12" y2="21" />
              </svg>
            </span>
          </div>
          <div className="stat-val">{stats?.total_scans ?? 0}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '6px' }}>
            Hồ sơ đã hiệu chỉnh: <strong style={{ color: 'var(--text-main)' }}>{stats?.edited_scans ?? 0}</strong>
          </p>
        </div>

        {/* CARD 2: PHÂN BỐ NGUỒN QUÉT */}
        <div className="card" style={{ padding: '20px' }}>
          <div className="stat-card-header">
            <span className="stat-label">Nguồn Đầu Vào</span>
            <span className="card-icon-badge" style={{ background: '#ecfdf5', color: 'var(--success)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
            <span className="badge badge-primary">Ảnh: {stats?.image_scans ?? 0}</span>
            <span className="badge badge-success">Cam: {stats?.webcam_scans ?? 0}</span>
            <span className="badge badge-warning">Video: {stats?.video_scans ?? 0}</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '10px' }}>
            Hỗ trợ tự động nhận diện cả 3 nguồn
          </p>
        </div>

        {/* CARD 3: ĐỘ TIN CẬY TRUNG BÌNH */}
        <div className="card" style={{ padding: '20px' }}>
          <div className="stat-card-header">
            <span className="stat-label">Độ Tin Cậy Trung Bình</span>
            <span className="card-icon-badge" style={{ background: '#fef3c7', color: '#b45309' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#b45309' }}>
            {stats?.avg_confidence ? `${stats.avg_confidence}%` : '0%'}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '6px' }}>
            Trừ điểm tỷ lệ khi người dùng sửa thủ công
          </p>
        </div>

        {/* CARD 4: THỜI GIAN XỬ LÝ */}
        <div className="card" style={{ padding: '20px' }}>
          <div className="stat-card-header">
            <span className="stat-label">Thời Gian Xử Lý TB</span>
            <span className="card-icon-badge" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#7c3aed' }}>
            {stats?.avg_processing_time ? `${stats.avg_processing_time}s` : '0s'}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '6px' }}>
            Bao gồm Detect 360° + Bóc tách 8 vùng + VietOCR
          </p>
        </div>
      </div>

      {/* BẢNG LỊCH SỬ CHỈNH SỬA & ĐÁNH GIÁ ĐỘ ĐÚNG AI */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <h2>
            <span className="card-title-left">
              <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </span>
              <span>Lịch Sử Đánh Giá Độ Đúng AI (Bảng ai_corrections)</span>
            </span>
            <span className="badge badge-warning">Đã ghi nhận: {corrections.length} chỉnh sửa</span>
          </h2>

          <button
            type="button"
            className="btn btn-outline"
            style={{ padding: '7px 14px', fontSize: '0.85rem' }}
            onClick={fetchStatsAndCorrections}
          >
            Làm mới số liệu
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
            ⏳ Đang nạp dữ liệu thống kê...
          </div>
        ) : corrections.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '2rem', marginBottom: '6px' }}>✨</div>
            <strong>Chưa có lần chỉnh sửa thủ công nào!</strong>
            <p style={{ marginTop: '4px', fontSize: '0.85rem' }}>
              Khi bạn sửa thông tin AI nhận diện tại Tab 1 và bấm Lưu, hệ thống sẽ lưu vết tại đây.
            </p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>Mã Lần</th>
                  <th>Trường Thông Tin</th>
                  <th>Dự Đoán Của AI (Cũ)</th>
                  <th>Người Dùng Sửa Thành (Mới)</th>
                  <th>Trạng Thái</th>
                  <th>Độ Tin Cậy AI</th>
                  <th>Thời Điểm</th>
                </tr>
              </thead>
              <tbody>
                {corrections.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: 700, color: 'var(--primary)' }}>#{c.history_id}</td>
                    <td>
                      <code style={{ background: '#f1f5f9', padding: '3px 6px', borderRadius: '4px', color: '#0f172a', fontWeight: 600 }}>
                        {c.field_name}
                      </code>
                    </td>
                    <td style={{ color: '#ef4444', textDecoration: 'line-through' }}>
                      {c.ai_prediction || '—'}
                    </td>
                    <td style={{ color: '#16a34a', fontWeight: 700 }}>
                      {c.user_corrected || '—'}
                    </td>
                    <td>
                      <span className="badge badge-warning">Cần Sửa</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      {c.ai_confidence ? `${Math.round(c.ai_confidence * 100)}%` : '—'}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {c.corrected_at ? new Date(c.corrected_at).toLocaleString('vi-VN') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
