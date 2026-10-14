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
    if (!window.confirm(`Bạn có chắc chắn muốn xóa hồ sơ CCCD #${id} (${idNumber}) không?`)) {
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

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
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
              <span>Bảng Lưu Kết Quả Thẻ CCCD ({total} hồ sơ)</span>
            </span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', margin: '4px 0 0 0' }}>
            Hệ thống lưu trữ 8 trường dữ liệu CCCD, hỗ trợ sửa, nạp lại vào Form Tab 1 và xuất file PDF.
          </p>
        </div>

        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder="Tìm theo Số CCCD hoặc Họ tên..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              padding: '8px 14px',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              fontSize: '0.88rem',
              width: '260px',
              outline: 'none',
            }}
          />
          <button type="submit" className="btn btn-primary" style={{ padding: '8px 14px' }}>
            Tìm Kiếm
          </button>
        </form>
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
          <table className="custom-table">
            <thead>
              <tr>
                <th style={{ width: '50px' }}>ID</th>
                <th style={{ width: '85px' }}>Ảnh Cắt</th>
                <th>Số CCCD (12 số)</th>
                <th>Họ và Tên</th>
                <th>Ngày Sinh</th>
                <th>Giới Tính</th>
                <th>Quê Quán</th>
                <th>Nơi Thường Trú</th>
                <th>Trạng Thái</th>
                <th style={{ width: '235px', textAlign: 'center' }}>Hành Động</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id}>
                  <td style={{ fontWeight: 700, color: 'var(--primary)' }}>#{row.id}</td>
                  <td>
                    <img
                      src={row.crop_image_path ? `${row.crop_image_path}?t=${row.id}` : '/media/cccd_fields_visualization.jpg'}
                      alt="Card Crop"
                      style={{ width: '64px', height: '40px', objectFit: 'cover', borderRadius: '4px', border: '1px solid var(--border-color)' }}
                      onError={(e) => { e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 40" fill="%23e4e6eb"><rect width="64" height="40"/><text x="50%" y="50%" fill="%2365676b" font-size="9" text-anchor="middle" dy=".3em">CCCD</text></svg>'; }}
                    />
                  </td>
                  <td>
                    <strong style={{ color: 'var(--primary)', letterSpacing: '0.5px' }}>{row.id_number}</strong>
                  </td>
                  <td style={{ fontWeight: 700, color: 'var(--text-main)' }}>{row.full_name}</td>
                  <td>{row.dob || '—'}</td>
                  <td>{row.gender || '—'}</td>
                  <td style={{ fontSize: '0.82rem', maxWidth: '170px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {row.origin_location || '—'}
                  </td>
                  <td style={{ fontSize: '0.82rem', maxWidth: '190px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {row.residence || '—'}
                  </td>
                  <td>
                    <span className={`badge ${row.status === 'EDITED' ? 'badge-warning' : 'badge-success'}`}>
                      {row.status === 'EDITED' ? 'Đã sửa' : 'AI Chuẩn'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: '5px', justifyContent: 'center', flexWrap: 'wrap' }}>
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '4px 8px', fontSize: '0.78rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                        title="Xem chi tiết & sửa hồ sơ"
                        onClick={() => onEditRecord(row)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px' }}><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                        Sửa
                      </button>
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '4px 8px', fontSize: '0.78rem', color: '#1877f2', borderColor: '#bfdbfe', background: '#eff6ff', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                        title="Tải lại vào Form Tab 1 để kiểm tra hoặc quét lại"
                        onClick={() => onLoadToScan && onLoadToScan(row)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px' }}><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
                        Nạp Form
                      </button>
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '4px 8px', fontSize: '0.78rem', color: '#dc2626', borderColor: '#fecaca', background: '#fef2f2', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                        title="Xuất phiếu thông tin và ảnh dưới dạng PDF"
                        onClick={() => exportCccdPdf(row)}
                      >
                        <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '12px', height: '12px', color: '#dc2626' }}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                        Xuất PDF
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger"
                        style={{ padding: '4px 8px', fontSize: '0.78rem' }}
                        title="Xóa hồ sơ khỏi CSDL"
                        onClick={() => handleDelete(row.id, row.id_number)}
                      >
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
