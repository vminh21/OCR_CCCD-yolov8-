// frontend/src/tabs/ResultsTab.jsx
import React, { useState, useEffect } from 'react';
import { apiGetResults, apiDeleteResult } from '../services/api';
import { exportCccdPdf } from '../utils/exportPdf';

export default function ResultsTab({ onEditRecord, onLoadToScan, showToast }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchResults = async (searchQuery = search) => {
    setLoading(true);
    try {
      const res = await apiGetResults(searchQuery, 50, 0);
      const data = await res.json();
      if (res.ok) {
        setItems(data.items || []);
        setTotal(data.total || 0);
      } else {
        showToast('❌ Không thể tải danh sách kết quả!', false);
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchResults(search);
  };

  const handleDelete = async (id, idNumber) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa hồ sơ CCCD #${id} (${idNumber}) khỏi hệ thống?`)) {
      return;
    }

    try {
      const res = await apiDeleteResult(id);
      if (res.ok) {
        showToast(`✅ Đã xóa thành công hồ sơ #${id}`, true);
        fetchResults();
      } else {
        const data = await res.json();
        showToast('❌ Lỗi xóa: ' + (data.detail || 'Thất bại'), false);
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối: ' + err.message, false);
    }
  };

  const formatVnDate = (dateStr) => {
    if (!dateStr) return '—';
    const clean = String(dateStr).trim();
    if (clean.includes('-')) {
      const parts = clean.split('-');
      if (parts.length === 3 && parts[0].length === 4) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
      }
    }
    return clean;
  };

  return (
    <div className="card">
      {/* HEADER CARD: TIÊU ĐỀ + TÌM KIẾM + LÀM MỚI (CHUẨN FACEBOOK UI) */}
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
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>
            </span>
            <span>Bảng Lưu Kết Quả Thẻ CCCD ({total} hồ sơ)</span>
          </span>
        </h2>

        <div className="search-filter-bar">
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px', flex: '1 1 auto' }}>
            <div style={{ position: 'relative', flex: '1 1 auto' }}>
              <input
                type="text"
                placeholder="Tìm theo Số CCCD hoặc Họ tên..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="search-input"
              />
              <svg
                className="svg-icon"
                viewBox="0 0 24 24"
                style={{
                  position: 'absolute',
                  left: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: '#94a3b8',
                }}
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </div>
            <button type="submit" className="btn btn-primary" style={{ padding: '8px 14px' }}>
              Tìm Kiếm
            </button>
          </form>

          <button
            type="button"
            className="btn btn-outline"
            style={{ padding: '8px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            title="Tải lại danh sách"
            onClick={() => {
              setSearch('');
              fetchResults('');
            }}
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '14px', height: '14px' }}>
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            Làm mới
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          ⏳ Đang tải dữ liệu hồ sơ từ cơ sở dữ liệu...
        </div>
      ) : items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>📂</div>
          <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>Chưa có hồ sơ CCCD nào được lưu</strong>
          <p style={{ marginTop: '4px', fontSize: '0.85rem' }}>Hãy tải ảnh hoặc quét thẻ tại Tab 1 để bắt đầu!</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table" style={{ margin: 0, border: 'none', borderRadius: 0 }}>
            <thead>
              <tr>
                <th style={{ width: '50px', textAlign: 'center' }}>#ID</th>
                <th style={{ width: '75px', textAlign: 'center' }}>Xem Thẻ</th>
                <th style={{ width: '135px' }}>Số CCCD</th>
                <th style={{ minWidth: '150px' }}>Họ Và Tên</th>
                <th style={{ width: '100px' }}>Ngày Sinh</th>
                <th style={{ width: '80px', textAlign: 'center' }}>Giới Tính</th>
                <th style={{ minWidth: '160px' }}>Quê Quán</th>
                <th style={{ minWidth: '170px' }}>Nơi Thường Trú</th>
                <th style={{ width: '90px', textAlign: 'center' }}>Trạng Thái</th>
                <th style={{ width: '215px', textAlign: 'center' }}>Thao Tác</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id}>
                  {/* #ID */}
                  <td style={{ textAlign: 'center', fontWeight: 700, color: 'var(--primary)' }}>
                    #{row.id}
                  </td>

                  {/* THUMBNAIL ẢNH CẮT */}
                  <td style={{ textAlign: 'center' }}>
                    <img
                      src={row.crop_image_path ? `${row.crop_image_path}?t=${row.id}` : '/media/cccd_fields_visualization.jpg'}
                      alt="Card Crop"
                      title="Bấm để xem và sửa chi tiết thẻ"
                      onClick={() => onEditRecord(row)}
                      style={{
                        width: '54px',
                        height: '34px',
                        objectFit: 'cover',
                        borderRadius: '4px',
                        border: '1px solid var(--border-color)',
                        cursor: 'pointer',
                        display: 'inline-block',
                        verticalAlign: 'middle',
                        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.transform = 'scale(1.1)';
                        e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.transform = 'scale(1)';
                        e.target.style.boxShadow = 'none';
                      }}
                      onError={(e) => {
                        e.target.src =
                          'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 54 34" fill="%23e4e6eb"><rect width="54" height="34"/><text x="50%" y="50%" fill="%2365676b" font-size="8" text-anchor="middle" dy=".3em">CCCD</text></svg>';
                      }}
                    />
                  </td>

                  {/* SỐ CCCD */}
                  <td>
                    <span
                      style={{
                        fontFamily: 'monospace, monospace',
                        fontWeight: 700,
                        color: 'var(--primary)',
                        fontSize: '0.92rem',
                        letterSpacing: '0.4px',
                      }}
                    >
                      {row.id_number}
                    </span>
                  </td>

                  {/* HỌ VÀ TÊN */}
                  <td style={{ fontWeight: 800, color: '#1c1e21', textTransform: 'uppercase', letterSpacing: '0.2px' }}>
                    {row.full_name}
                  </td>

                  {/* NGÀY SINH (DD/MM/YYYY) */}
                  <td style={{ whiteSpace: 'nowrap', color: '#475569', fontWeight: 500 }}>
                    {formatVnDate(row.dob)}
                  </td>

                  {/* GIỚI TÍNH */}
                  <td style={{ textAlign: 'center' }}>
                    {row.gender ? (
                      <span
                        className="badge"
                        style={{
                          background: row.gender.toUpperCase().includes('NAM') ? '#eff6ff' : '#fdf2f8',
                          color: row.gender.toUpperCase().includes('NAM') ? '#1d4ed8' : '#be185d',
                          border: `1px solid ${row.gender.toUpperCase().includes('NAM') ? '#bfdbfe' : '#fbcfe8'}`,
                        }}
                      >
                        {row.gender}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>

                  {/* QUÊ QUÁN */}
                  <td
                    style={{
                      maxWidth: '180px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      color: '#475569',
                      fontSize: '0.84rem',
                    }}
                    title={row.origin_location || ''}
                  >
                    {row.origin_location || '—'}
                  </td>

                  {/* NƠI THƯỜNG TRÚ */}
                  <td
                    style={{
                      maxWidth: '190px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      color: '#475569',
                      fontSize: '0.84rem',
                    }}
                    title={row.residence || ''}
                  >
                    {row.residence || '—'}
                  </td>

                  {/* TRẠNG THÁI */}
                  <td style={{ textAlign: 'center' }}>
                    <span className={`badge ${row.status === 'EDITED' ? 'badge-warning' : 'badge-success'}`}>
                      {row.status === 'EDITED' ? 'Đã sửa' : 'AI Chuẩn'}
                    </span>
                  </td>

                  {/* HÀNH ĐỘNG: 3 NÚT GỌN GÀNG (SỬA • XUẤT PDF • XÓA) */}
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: '5px', justifyContent: 'center', alignItems: 'center' }}>
                      {/* SỬA */}
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{
                          padding: '4px 8px',
                          fontSize: '0.78rem',
                          height: '28px',
                          whiteSpace: 'nowrap',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                        }}
                        title="Xem chi tiết, sửa hoặc nạp vào form"
                        onClick={() => onEditRecord(row)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px', color: 'var(--primary)' }}>
                          <path d="M12 20h9" />
                          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                        </svg>
                        Sửa
                      </button>

                      {/* XUẤT PDF */}
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{
                          padding: '4px 8px',
                          fontSize: '0.78rem',
                          height: '28px',
                          color: '#dc2626',
                          borderColor: '#fecaca',
                          background: '#fef2f2',
                          whiteSpace: 'nowrap',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                        }}
                        title="Xuất phiếu thông tin và ảnh dưới dạng PDF"
                        onClick={() => exportCccdPdf(row)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px', color: '#dc2626' }}>
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" />
                          <line x1="16" y1="17" x2="8" y2="17" />
                          <line x1="10" y1="9" x2="8" y2="9" />
                        </svg>
                        Xuất PDF
                      </button>

                      {/* XÓA */}
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{
                          padding: '4px 7px',
                          fontSize: '0.78rem',
                          height: '28px',
                          color: '#ef4444',
                          borderColor: '#fca5a5',
                          background: '#ffffff',
                          whiteSpace: 'nowrap',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '2px',
                        }}
                        title="Xóa hồ sơ khỏi CSDL"
                        onClick={() => handleDelete(row.id, row.id_number)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px', color: '#ef4444' }}>
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                        Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
