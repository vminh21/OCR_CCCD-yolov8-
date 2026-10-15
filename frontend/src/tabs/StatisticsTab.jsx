// frontend/src/tabs/StatisticsTab.jsx
import React, { useState, useEffect } from 'react';
import { apiGetStatistics, apiGetDemographics } from '../services/api';

export default function StatisticsTab({ showToast }) {
  const [stats, setStats] = useState(null);
  const [demographics, setDemographics] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resStat, resDemo] = await Promise.all([
        apiGetStatistics(),
        apiGetDemographics(),
      ]);

      if (resStat.ok) {
        const dataStat = await resStat.json();
        setStats(dataStat);
      }
      if (resDemo.ok) {
        const dataDemo = await resDemo.json();
        setDemographics(dataDemo);
      }
    } catch (err) {
      if (showToast) showToast('❌ Lỗi tải thống kê: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalScans = stats?.total_scans || 0;
  const imageScans = stats?.image_scans ?? 0;
  const webcamScans = stats?.webcam_scans ?? 0;
  const videoScans = stats?.video_scans ?? 0;

  const totalRecords = demographics?.total_records || 0;
  const genderStats = demographics?.gender_stats || [];
  const provinceStats = demographics?.province_stats || [];
  const ageGroupStats = demographics?.age_group_stats || [];

  const maleStat = genderStats.find((g) => g.name === 'Nam') || { count: 0, percent: 0 };
  const femaleStat = genderStats.find((g) => g.name === 'Nữ') || { count: 0, percent: 0 };
  const otherGenderStat = genderStats.find((g) => g.name === 'Khác') || { count: 0, percent: 0 };

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
              background: '#eff6ff',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '22px', height: '22px' }}>
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              Thống Kê Lượt Quét & Phân Tích Nhân Khẩu Học
            </h2>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              Dữ liệu tổng hợp từ các lượt quét ảnh, webcam, video và cơ sở dữ liệu {totalRecords} hồ sơ CCCD
            </p>
          </div>
        </div>

        <button
          type="button"
          className="btn btn-outline"
          disabled={loading}
          onClick={fetchData}
          title="Tải lại số liệu mới nhất"
        >
          <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '14px', height: '14px' }}>
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
          {loading ? 'Đang tải...' : 'Làm mới'}
        </button>
      </div>

      {/* 4 THẺ KPI LƯỢT QUÉT (FACEBOOK FEED STYLE) */}
      <div className="stats-grid">
        {/* CARD 1: TỔNG SỐ LƯỢT QUÉT */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Tổng Lượt Quét</span>
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <rect x="3" y="3" width="18" height="18" rx="4" />
                <circle cx="12" cy="12" r="3.5" />
              </svg>
            </span>
          </div>
          <div className="stat-val">{totalScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Hồ sơ CCCD đã lưu: <strong style={{ color: 'var(--primary)' }}>{totalRecords}</strong>
          </p>
        </div>

        {/* CARD 2: QUÉT BẰNG ẢNH */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Quét Qua Ảnh</span>
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: '#1d4ed8' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#1d4ed8' }}>{imageScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tỷ lệ nguồn: <strong style={{ color: '#1d4ed8' }}>{totalScans > 0 ? ((imageScans / totalScans) * 100).toFixed(1) : 0}%</strong>
          </p>
        </div>

        {/* CARD 3: QUÉT BẰNG WEBCAM */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Quét Qua Webcam</span>
            <span className="card-icon-badge" style={{ background: '#ecfdf5', color: '#059669' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M23 7l-7 5 7 5V7z" />
                <rect x="1" y="5" width="15" height="14" rx="3" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#059669' }}>{webcamScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tỷ lệ nguồn: <strong style={{ color: '#059669' }}>{totalScans > 0 ? ((webcamScans / totalScans) * 100).toFixed(1) : 0}%</strong>
          </p>
        </div>

        {/* CARD 4: QUÉT BẰNG VIDEO */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">Quét Qua Video</span>
            <span className="card-icon-badge" style={{ background: '#fffbeb', color: '#d97706' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            </span>
          </div>
          <div className="stat-val" style={{ color: '#d97706' }}>{videoScans}</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '6px', fontWeight: 500 }}>
            Tỷ lệ nguồn: <strong style={{ color: '#d97706' }}>{totalScans > 0 ? ((videoScans / totalScans) * 100).toFixed(1) : 0}%</strong>
          </p>
        </div>
      </div>

      {/* KHUNG PHÂN TÍCH NHÂN KHẨU HỌC: 2 CỘT */}
      <div className="demographics-grid">
        {/* KHUNG 1: TỈ LỆ GIỚI TÍNH (NAM / NỮ) */}
        <div className="card">
          <h2>
            <span className="card-title-left">
              <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </span>
              <span>1. Tỉ Lệ Giới Tính (Nam / Nữ)</span>
            </span>
            <span className="badge badge-primary">{totalRecords} hồ sơ</span>
          </h2>

          <div style={{ marginTop: '16px' }}>
            {/* THANH TỔNG HỢP SONG SONG NAM / NỮ */}
            <div
              style={{
                width: '100%',
                height: '16px',
                borderRadius: '8px',
                overflow: 'hidden',
                display: 'flex',
                background: '#e4e6eb',
                marginBottom: '16px',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)',
              }}
            >
              <div
                style={{
                  width: `${maleStat.percent}%`,
                  background: '#1877f2',
                  transition: 'width 0.4s ease',
                }}
                title={`Nam: ${maleStat.percent}%`}
              />
              <div
                style={{
                  width: `${femaleStat.percent}%`,
                  background: '#ec4899',
                  transition: 'width 0.4s ease',
                }}
                title={`Nữ: ${femaleStat.percent}%`}
              />
              <div
                style={{
                  width: `${otherGenderStat.percent}%`,
                  background: '#94a3b8',
                  transition: 'width 0.4s ease',
                }}
                title={`Khác: ${otherGenderStat.percent}%`}
              />
            </div>

            {/* CHI TIẾT TỪNG GIỚI TÍNH */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {/* NAM */}
              <div className="demographic-item">
                <div className="demographic-header">
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#1877f2', display: 'inline-block' }} />
                    Nam giới
                  </span>
                  <span style={{ fontWeight: 700, color: '#1877f2' }}>
                    {maleStat.count} người ({maleStat.percent}%)
                  </span>
                </div>
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${maleStat.percent}%`, background: '#1877f2' }} />
                </div>
              </div>

              {/* NỮ */}
              <div className="demographic-item">
                <div className="demographic-header">
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ec4899', display: 'inline-block' }} />
                    Nữ giới
                  </span>
                  <span style={{ fontWeight: 700, color: '#ec4899' }}>
                    {femaleStat.count} người ({femaleStat.percent}%)
                  </span>
                </div>
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${femaleStat.percent}%`, background: '#ec4899' }} />
                </div>
              </div>

              {/* KHÁC / CHƯA XÁC ĐỊNH */}
              {otherGenderStat.count > 0 && (
                <div className="demographic-item">
                  <div className="demographic-header">
                    <span style={{ fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#94a3b8', display: 'inline-block' }} />
                      Chưa rõ
                    </span>
                    <span style={{ fontWeight: 700, color: '#64748b' }}>
                      {otherGenderStat.count} người ({otherGenderStat.percent}%)
                    </span>
                  </div>
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{ width: `${otherGenderStat.percent}%`, background: '#94a3b8' }} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* KHUNG 2: PHÂN BỐ ĐỘ TUỔI & NĂM SINH */}
        <div className="card">
          <h2>
            <span className="card-title-left">
              <span className="card-icon-badge" style={{ background: '#ecfdf5', color: '#059669' }}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </span>
              <span>2. Thống Kê Năm Sinh & Nhóm Độ Tuổi</span>
            </span>
            <span className="badge badge-success">Theo chuẩn CCCD</span>
          </h2>

          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {ageGroupStats.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', textAlign: 'center', padding: '20px 0' }}>
                Chưa có dữ liệu năm sinh
              </p>
            ) : (
              ageGroupStats.map((item, idx) => {
                const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#64748b', '#94a3b8'];
                const color = colors[idx % colors.length];
                return (
                  <div key={item.label} className="demographic-item">
                    <div className="demographic-header">
                      <span style={{ fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: color, display: 'inline-block' }} />
                        {item.label}
                      </span>
                      <span style={{ fontWeight: 700, color: color }}>
                        {item.count} người ({item.percent}%)
                      </span>
                    </div>
                    <div className="progress-bar-bg">
                      <div className="progress-bar-fill" style={{ width: `${item.percent}%`, background: color }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* KHUNG 3: PHÂN BỐ TỈNH THÀNH (63 TỈNH THÀNH VIỆT NAM) */}
      <div className="card">
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </span>
            <span>3. Phân Bố Tỉnh / Thành Phố Căn Cước ({provinceStats.length} tỉnh/thành ghi nhận)</span>
          </span>
          <span className="badge" style={{ background: '#f5f3ff', color: '#7c3aed', border: '1px solid #ddd6fe' }}>
            Nơi Thường Trú & Quê Quán
          </span>
        </h2>

        {provinceStats.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', textAlign: 'center', padding: '30px 0' }}>
            Chưa có thông tin địa chỉ tỉnh thành nào được quét
          </p>
        ) : (
          <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {provinceStats.map((item, idx) => (
              <div
                key={item.province}
                style={{
                  background: '#f8fafc',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '12px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--primary)', marginRight: '6px' }}>#{idx + 1}</span>
                    {item.province}
                  </span>
                  <span style={{ fontWeight: 700, color: 'var(--primary)', fontSize: '0.88rem' }}>
                    {item.count} hồ sơ ({item.percent}%)
                  </span>
                </div>
                <div className="progress-bar-bg" style={{ height: '7px' }}>
                  <div
                    className="progress-bar-fill"
                    style={{
                      width: `${item.percent}%`,
                      background: idx === 0 ? 'var(--primary)' : idx === 1 ? '#059669' : '#6366f1',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
