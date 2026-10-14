// frontend/src/tabs/ResultsTab.jsx
import React, { useState, useEffect } from 'react';
import { apiGetResults, apiDeleteResult } from '../services/api';

export default function ResultsTab({ onEditRecord, showToast }) {
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <h2>
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
            <span>Bảng Dữ Liệu Hồ Sơ CCCD (CSDL PostgreSQL: cccd_results)</span>
          </span>
          <span className="badge badge-primary">Tổng: {total} hồ sơ</span>
        </h2>

        {/* SEARCH FORM */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder="Tìm theo CCCD, họ tên..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '240px', padding: '8px 12px', fontSize: '0.9rem' }}
          />
          <button type="submit" className="btn btn-outline" style={{ padding: '8px 14px' }}>
            <svg className="svg-icon" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            Tìm
          </button>
          <button
            type="button"
            className="btn btn-outline"
            style={{ padding: '8px 12px' }}
            onClick={() => { setSearch(''); fetchResults(''); }}
          >
            Làm mới
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
                <th style={{ width: '90px' }}>Ảnh Cắt</th>
                <th>Số CCCD (12 số)</th>
                <th>Họ và Tên</th>
                <th>Ngày Sinh</th>
                <th>Giới Tính</th>
                <th>Quê Quán</th>
                <th>Nơi Thường Trú</th>
                <th>Trạng Thái</th>
                <th style={{ width: '130px', textAlign: 'center' }}>Hành Động</th>
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
                  <td style={{ fontSize: '0.82rem', maxWidth: '180px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {row.origin_location || '—'}
                  </td>
                  <td style={{ fontSize: '0.82rem', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {row.residence || '—'}
                  </td>
                  <td>
                    <span className={`badge ${row.status === 'EDITED' ? 'badge-warning' : 'badge-success'}`}>
                      {row.status === 'EDITED' ? 'Đã sửa' : 'AI Chuẩn'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '5px 9px', fontSize: '0.8rem' }}
                        title="Xem và sửa hồ sơ"
                        onClick={() => onEditRecord(row)}
                      >
                        Sửa
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger"
                        style={{ padding: '5px 9px', fontSize: '0.8rem' }}
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
