// frontend/src/components/EditModal.jsx
import React, { useState, useEffect } from 'react';
import { apiUpdateResult } from '../services/api';

export default function EditModal({ isOpen, record, onClose, onSaveSuccess, onOpenInScanTab, showToast }) {
  const [formData, setFormData] = useState({
    id_number: '',
    full_name: '',
    dob: '',
    gender: '',
    nationality: 'Việt Nam',
    origin_location: '',
    residence: '',
    expiry_date: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (record) {
      setFormData({
        id_number: record.id_number || '',
        full_name: record.full_name || '',
        dob: record.dob || '',
        gender: record.gender || '',
        nationality: record.nationality || 'Việt Nam',
        origin_location: record.origin_location || '',
        residence: record.residence || '',
        expiry_date: record.expiry_date || '',
      });
    }
  }, [record]);

  if (!isOpen || !record) return null;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await apiUpdateResult(record.id, formData);
      const data = await res.json();
      if (res.ok) {
        showToast('✅ Đã cập nhật thông tin hồ sơ CCCD!', true);
        onSaveSuccess(data);
        onClose();
      } else {
        showToast('❌ Lỗi cập nhật: ' + (data.detail || 'Thất bại'), false);
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="modal-view-detail" className="modal active">
      <div className="modal-content" style={{ maxWidth: '850px', width: '95%', padding: '24px', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ color: 'var(--primary)' }}>#ID {record.id}</span> • Chi Tiết & Chỉnh Sửa Hồ Sơ CCCD
          </h3>
          <button type="button" className="btn btn-outline" style={{ padding: '4px 10px' }} onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            <div className="field-group">
              <label>1. Số Căn cước công dân (12 số)</label>
              <input
                type="text"
                required
                value={formData.id_number}
                onChange={(e) => handleChange('id_number', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>2. Họ và tên</label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>3. Ngày sinh (DD/MM/YYYY)</label>
              <input
                type="text"
                value={formData.dob}
                onChange={(e) => handleChange('dob', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>4. Giới tính</label>
              <input
                type="text"
                value={formData.gender}
                onChange={(e) => handleChange('gender', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>5. Quốc tịch</label>
              <input
                type="text"
                value={formData.nationality}
                onChange={(e) => handleChange('nationality', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>8. Có giá trị đến (DD/MM/YYYY)</label>
              <input
                type="text"
                value={formData.expiry_date}
                onChange={(e) => handleChange('expiry_date', e.target.value)}
              />
            </div>
          </div>

          <div className="field-group" style={{ marginTop: '14px' }}>
            <label>6. Quê quán</label>
            <textarea
              rows={2}
              value={formData.origin_location}
              onChange={(e) => handleChange('origin_location', e.target.value)}
            />
          </div>

          <div className="field-group" style={{ marginTop: '14px' }}>
            <label>7. Nơi thường trú</label>
            <textarea
              rows={2}
              value={formData.residence}
              onChange={(e) => handleChange('residence', e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '24px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => {
                onClose();
                onOpenInScanTab(record);
              }}
            >
              Tải vào Form Tab 1 để quét lại
            </button>
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Đang lưu...' : 'Lưu Thay Đổi'}
            </button>
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Đóng
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
