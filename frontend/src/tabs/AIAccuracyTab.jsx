// frontend/src/tabs/AIAccuracyTab.jsx
import React, { useState, useEffect } from 'react';
import { apiGetAIQuality, apiGetCorrections, getUserAIKey } from '../services/api';


export default function AIAccuracyTab({ showToast }) {
  const [aiQuality, setAiQuality] = useState(null);
  const [corrections, setCorrections] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchQualityData = async () => {
    setLoading(true);
    try {
      const [resQuality, resCorr] = await Promise.all([
        apiGetAIQuality(),
        apiGetCorrections(),
      ]);

      if (resQuality.ok) {
        const dataQuality = await resQuality.json();
        setAiQuality(dataQuality);
      }
      if (resCorr.ok) {
        const dataCorr = await resCorr.json();
        setCorrections(dataCorr || []);
      }
    } catch (err) {
      if (showToast) showToast('❌ Lỗi tải dữ liệu đánh giá AI: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQualityData();
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

  const totalScans = aiQuality?.total_scans || 0;
  const editedScans = aiQuality?.edited_scans || 0;
  const perfectScans = aiQuality?.perfect_scans || 0;
  const perfectRate = aiQuality?.perfect_rate ?? (totalScans > 0 ? (((totalScans - editedScans) / totalScans) * 100).toFixed(1) : 100);
  const avgConfidence = aiQuality?.avg_confidence ? `${Number(aiQuality.avg_confidence).toFixed(1)}%` : '0%';
  const avgTime = aiQuality?.avg_processing_time ? `${aiQuality.avg_processing_time}s` : '0s';
  const fieldAccuracy = aiQuality?.field_accuracy || [];

  return (
    <div>
      {/* HEADER: TIÊU ĐỀ & LÀM MỚI */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '8px',
              background: '#ecfdf5',
              color: '#059669',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '22px', height: '22px' }}>
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              Đánh Giá Độ Đúng & Chất Lượng Mô Hình AI (YOLOv8 + VietOCR)
            </h2>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              Đo lường độ tin cậy, tỷ lệ chính xác từng trường và đối soát các lần hiệu chỉnh thực tế
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: '12px',
              background: getUserAIKey() ? '#e0f2fe' : '#ecfdf5',
              color: getUserAIKey() ? '#0369a1' : '#047857',
              border: `1px solid ${getUserAIKey() ? '#bae6fd' : '#a7f3d0'}`
            }}
            title="Quản lý và đổi API Key tại Tab Hồ Sơ Cá Nhân"
          >
            {getUserAIKey() ? '🔑 Đang dùng Key cá nhân' : '🌐 Dùng Key mặc định (.env)'}
          </span>

          <button
            type="button"
            className="btn btn-outline"
            disabled={loading}
            onClick={fetchQualityData}
            title="Tải lại số liệu đánh giá mới nhất"
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '14px', height: '14px' }}>
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            {loading ? 'Đang tải...' : 'Làm mới số liệu'}
          </button>
        </div>
      </div>


      {/* 4 THẺ KPI CHẤT LƯỢNG AI */}
      <div className="stats-grid">
        {/* CARD 1: ĐỘ TIN CẬY TRUNG BÌNH */}
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
          <div className="stat-val" style={{ color: '#059669' }}>{avgConfidence}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Điểm tự tin trung bình của mạng VietOCR
          </p>
        </div>

        {/* CARD 2: TỶ LỆ CHUẨN XÁC 100% */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Tỷ Lệ Nhận Diện Chuẩn 100%</span>
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: 'var(--primary)' }}>{perfectRate}%</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            <strong style={{ color: 'var(--primary)' }}>{perfectScans}</strong> / {totalScans} lượt quét không cần sửa
          </p>
        </div>

        {/* CARD 3: SỐ CA CẦN HIỆU CHỈNH */}
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
          <div className="stat-val" style={{ color: '#d97706' }}>{editedScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tỷ lệ can thiệp: <strong style={{ color: '#d97706' }}>{totalScans > 0 ? ((editedScans / totalScans) * 100).toFixed(1) : 0}%</strong>
          </p>
        </div>

        {/* CARD 4: THỜI GIAN XỬ LÝ TRUNG BÌNH */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Thời Gian Xử Lý TB</span>
            <span className="card-icon-badge" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 14 14" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#7c3aed' }}>{avgTime}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tốc độ suy luận YOLOv8 + VietOCR
          </p>
        </div>
      </div>

      {/* KHUNG PHÂN TÍCH ĐỘ CHÍNH XÁC THEO TỪNG TRƯỜNG THÔNG TIN */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </span>
            <span>Độ Chính Xác Nhận Diện Của AI Theo Từng Trường (Đủ 8 trường)</span>
          </span>
          <span className="badge badge-success">Khoa Học Thực Nghiệm</span>
        </h2>

        <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
          {fieldAccuracy.map((f) => {
            const isHigh = f.accuracy_percent >= 98;
            const isMedium = f.accuracy_percent >= 90 && f.accuracy_percent < 98;
            const barColor = isHigh ? '#10b981' : isMedium ? '#3b82f6' : '#f59e0b';

            return (
              <div
                key={f.field_name}
                style={{
                  background: '#f8fafc',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '12px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.88rem' }}>
                    {f.field_label}
                  </span>
                  <span style={{ fontWeight: 700, color: barColor, fontSize: '0.88rem' }}>
                    {f.accuracy_percent}%
                  </span>
                </div>
                <div className="progress-bar-bg" style={{ height: '7px', marginBottom: '6px' }}>
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${f.accuracy_percent}%`, background: barColor }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>Số lần người dùng sửa: <strong style={{ color: f.error_count > 0 ? '#d97706' : '#059669' }}>{f.error_count}</strong></span>
                  <span>{f.error_count === 0 ? '✅ Hoàn hảo' : '⚠️ Có can thiệp'}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* BẢNG ĐỐI SOÁT CHI TIẾT CÁC LẦN HIỆU CHỈNH THỰC TẾ */}
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
              <span className="card-icon-badge" style={{ background: '#fef2f2', color: '#dc2626' }}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <polygon points="12 2 2 7 12 12 22 7 12 2" />
                  <polyline points="2 17 12 22 22 17" />
                  <polyline points="2 12 12 17 22 12" />
                </svg>
              </span>
              <span>Bảng Đối Soát Lịch Sử Chỉnh Sửa ({corrections.length} lần can thiệp)</span>
            </span>
          </h2>
          <span className="badge" style={{ background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
            Học Máy & Tối Ưu Mô Hình
          </span>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
            ⏳ Đang tải dữ liệu lịch sử đối soát AI...
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

                    {/* AI NHẬN DIỆN BAN ĐẦU (GẠCH ĐỎ) */}
                    <td>
                      <span
                        style={{
                          color: '#dc2626',
                          textDecoration: 'line-through',
                          background: '#fef2f2',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 600,
                          fontSize: '0.86rem',
                          border: '1px solid #fee2e2',
                          display: 'inline-block',
                          maxWidth: '220px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={c.ai_prediction || 'Trống'}
                      >
                        {c.ai_prediction || '— (Trống)'}
                      </span>
                    </td>

                    {/* NGƯỜI DÙNG SỬA LẠI (HIGHLIGHT XANH LÁ) */}
                    <td>
                      <span
                        style={{
                          color: '#15803d',
                          background: '#f0fdf4',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 700,
                          fontSize: '0.86rem',
                          border: '1px solid #dcfce7',
                          display: 'inline-block',
                          maxWidth: '220px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={c.user_corrected}
                      >
                        {c.user_corrected}
                      </span>
                    </td>

                    {/* ĐÁNH GIÁ AI */}
                    <td style={{ textAlign: 'center' }}>
                      <span className="badge badge-warning" style={{ background: '#fffbeb', color: '#b45309', border: '1px solid #fde68a' }}>
                        ⚠️ AI Đoán Sai
                      </span>
                    </td>

                    {/* ĐỘ TIN CẬY CỦA AI */}
                    <td style={{ textAlign: 'center', fontWeight: 600, color: 'var(--text-muted)' }}>
                      {c.ai_confidence ? `${(Number(c.ai_confidence) * 100).toFixed(1)}%` : '—'}
                    </td>

                    {/* THỜI ĐIỂM SỬA */}
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
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
