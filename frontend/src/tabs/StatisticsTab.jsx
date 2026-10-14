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
      if (showToast) showToast('❌ Lỗi tải thống kê: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatsAndCorrections();
  }, []);

  const getFieldLabel = (fieldName) => {
    const map = {
      id_number: '1. Số CCCD',
      so_cccd: '1. Số CCCD',
      full_name: '2. Họ và tên',
      ho_ten: '2. Họ và tên',
      dob: '3. Ngày sinh',
      ngay_sinh: '3. Ngày sinh',
      gender: '4. Giới tính',
      gioi_tinh: '4. Giới tính',
      nationality: '5. Quốc tịch',
      quoc_tich: '5. Quốc tịch',
      origin_location: '6. Quê quán',
      que_quan: '6. Quê quán',
      residence: '7. Nơi thường trú',
      noi_ctru: '7. Nơi thường trú',
      expiry_date: '8. Có giá trị đến',
      ngay_het_han: '8. Có giá trị đến',
    };
    return map[fieldName] || fieldName;
  };

  const formatDateTimeVN = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    } catch {
      return isoStr;
    }
  };

  const totalScans = stats?.total_scans || 0;
  const editedScans = stats?.edited_scans || 0;
  const editRate = totalScans > 0 ? ((editedScans / totalScans) * 100).toFixed(1) : 0;
  const avgConfidence = stats?.avg_confidence ? `${Number(stats.avg_confidence).toFixed(1)}%` : '0%';
  const imageScans = stats?.image_scans ?? 0;
  const webcamScans = stats?.webcam_scans ?? 0;
  const videoScans = stats?.video_scans ?? 0;

  return (
    <div>
      {/* 4 STAT CARDS CHUẨN FACEBOOK DESIGN SYSTEM */}
      <div className="stats-grid">
        {/* CARD 1: TỔNG SỐ LƯỢT QUÉT */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Tổng Số Lượt Quét</span>
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </span>
          </div>
          <div className="stat-val">{totalScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Hồ sơ đã lưu: <strong style={{ color: 'var(--primary)' }}>{totalScans}</strong> • Đã sửa: <strong style={{ color: '#d97706' }}>{editedScans}</strong>
          </p>
        </div>

        {/* CARD 2: PHÂN BỔ NGUỒN ĐẦU VÀO */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Ảnh / Webcam / Video</span>
            <span className="card-icon-badge" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M23 7l-7 5 7 5V7z" />
                <rect x="1" y="5" width="15" height="14" rx="3" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ fontSize: '1.75rem', color: '#6366f1' }}>
            {imageScans} <span style={{ fontSize: '1.1rem', color: '#94a3b8' }}>/</span> {webcamScans} <span style={{ fontSize: '1.1rem', color: '#94a3b8' }}>/</span> {videoScans}
          </div>
          <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
            <span className="badge" style={{ background: '#eff6ff', color: '#1d4ed8', border: '1px solid #bfdbfe' }}>Ảnh: {imageScans}</span>
            <span className="badge" style={{ background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0' }}>Cam: {webcamScans}</span>
            <span className="badge" style={{ background: '#fffbeb', color: '#d97706', border: '1px solid #fde68a' }}>Video: {videoScans}</span>
          </div>
        </div>

        {/* CARD 3: SỐ CA HIỆU CHỈNH & TỶ LỆ */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Số Ca Phải Hiệu Chỉnh</span>
            <span className="card-icon-badge" style={{ background: '#fffbeb', color: '#d97706' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#d97706' }}>
            {editedScans}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tỷ lệ cần can thiệp: <strong style={{ color: '#d97706' }}>{editRate}%</strong> (Tự động phạt điểm)
          </p>
        </div>

        {/* CARD 4: ĐỘ TIN CẬY TRUNG BÌNH */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Độ Tin Cậy AI Trung Bình</span>
            <span className="card-icon-badge" style={{ background: '#ecfdf5', color: '#059669' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 14 14" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#059669' }}>
            {avgConfidence}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Thời gian xử lý TB: <strong style={{ color: '#0f172a' }}>{stats?.avg_processing_time ? `${stats.avg_processing_time}s` : '0s'}</strong>
          </p>
        </div>
      </div>

      {/* BẢNG LỊCH SỬ CHỈNH SỬA & ĐÁNH GIÁ ĐỘ ĐÚNG AI */}
      <div className="card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <h2 style={{ margin: 0, padding: 0 }}>
            <span className="card-title-left">
              <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <line x1="10" y1="9" x2="8" y2="9" />
                </svg>
              </span>
              <span>Bảng Đối Soát Độ Đúng Của AI & Người Dùng Sửa Gì (ai_corrections)</span>
            </span>
            <span className="badge badge-warning">Đã ghi nhận: {corrections.length} chỉnh sửa</span>
          </h2>

          <button
            type="button"
            className="btn btn-outline"
            style={{ padding: '8px 14px', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            onClick={fetchStatsAndCorrections}
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '14px', height: '14px' }}>
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            Làm mới số liệu
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
            ⏳ Đang tải số liệu thống kê và lịch sử sửa đổi...
          </div>
        ) : corrections.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '45px 20px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>✨</div>
            <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>Chưa có lần chỉnh sửa thủ công nào!</strong>
            <p style={{ marginTop: '4px', fontSize: '0.85rem' }}>
              Khi người dùng chỉnh sửa thông tin AI nhận diện tại Tab 1 hoặc Tab 2 và bấm Lưu, hệ thống sẽ lưu vết so sánh chi tiết tại đây.
            </p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table" style={{ margin: 0, border: 'none', borderRadius: 0 }}>
              <thead>
                <tr>
                  <th style={{ width: '70px', textAlign: 'center' }}>Lượt Quét #</th>
                  <th style={{ width: '170px' }}>Trường Bị Sửa</th>
                  <th style={{ minWidth: '180px' }}>AI Nhận Diện Ban Đầu</th>
                  <th style={{ minWidth: '180px' }}>Người Dùng Sửa Lại</th>
                  <th style={{ width: '110px', textAlign: 'center' }}>Đánh Giá AI</th>
                  <th style={{ width: '110px', textAlign: 'center' }}>Độ Tin Cậy AI</th>
                  <th style={{ width: '160px' }}>Thời Điểm Sửa</th>
                </tr>
              </thead>
              <tbody>
                {corrections.map((c) => (
                  <tr key={c.id}>
                    {/* MÃ LƯỢT QUÉT */}
                    <td style={{ textAlign: 'center', fontWeight: 700, color: 'var(--primary)' }}>
                      #{c.history_id || c.scan_id || c.id}
                    </td>

                    {/* TRƯỜNG THÔNG TIN */}
                    <td>
                      <span
                        style={{
                          background: '#f1f5f9',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          color: '#0f172a',
                          fontWeight: 700,
                          fontSize: '0.82rem',
                          border: '1px solid #e2e8f0',
                          display: 'inline-block',
                        }}
                      >
                        {getFieldLabel(c.field_name)}
                      </span>
                    </td>

                    {/* AI NHẬN DIỆN BAN ĐẦU */}
                    <td>
                      <span
                        style={{
                          color: '#dc2626',
                          background: '#fef2f2',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          border: '1px solid #fee2e2',
                          textDecoration: 'line-through',
                          fontSize: '0.85rem',
                          display: 'inline-block',
                          maxWidth: '220px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                        title={c.ai_prediction || 'Chưa nhận diện'}
                      >
                        {c.ai_prediction || '— (Trống)'}
                      </span>
                    </td>

                    {/* NGƯỜI DÙNG SỬA LẠI */}
                    <td>
                      <span
                        style={{
                          color: '#15803d',
                          background: '#f0fdf4',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          border: '1px solid #bbf7d0',
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          display: 'inline-block',
                          maxWidth: '220px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                        title={c.user_corrected || ''}
                      >
                        {c.user_corrected || '—'}
                      </span>
                    </td>

                    {/* ĐÁNH GIÁ AI */}
                    <td style={{ textAlign: 'center' }}>
                      <span className="badge badge-warning">
                        Cần sửa
                      </span>
                    </td>

                    {/* ĐỘ TIN CẬY AI */}
                    <td style={{ textAlign: 'center' }}>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          color: c.ai_confidence && c.ai_confidence >= 0.8 ? '#15803d' : '#d97706',
                        }}
                      >
                        {c.ai_confidence ? `${Math.round(c.ai_confidence * 100)}%` : '—'}
                      </span>
                    </td>

                    {/* THỜI ĐIỂM SỬA */}
                    <td style={{ color: '#475569', fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
                      {formatDateTimeVN(c.corrected_at)}
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
