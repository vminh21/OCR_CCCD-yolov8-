// frontend/src/components/ChangePasswordModal.jsx
import React, { useState } from 'react';
import { apiChangePassword } from '../services/api';

export default function ChangePasswordModal({ isOpen, onClose, showToast }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      showToast('❌ Mật khẩu mới và xác nhận mật khẩu không khớp!', false);
      return;
    }
    if (newPassword.length < 6) {
      showToast('❌ Mật khẩu mới phải có tối thiểu 6 ký tự!', false);
      return;
    }

    setLoading(true);
    try {
      const res = await apiChangePassword(oldPassword, newPassword);
      const data = await res.json();
      if (res.ok) {
        showToast('✅ Đổi mật khẩu thành công!', true);
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        onClose();
      } else {
        showToast('❌ Lỗi: ' + (data.detail || 'Không thể đổi mật khẩu'), false);
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối: ' + err.message, false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="modal-password" className="modal active">
      <div className="modal-content">
        <h3 style={{ marginBottom: '18px', fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg className="svg-icon" viewBox="0 0 24 24" style={{ color: '#6366f1' }}>
            <circle cx="7.5" cy="15.5" r="4.5" />
            <path d="m21 3-9.5 9.5" />
            <path d="m15.5 7.5 3 3" />
            <path d="m18.5 4.5 2 2" />
          </svg>
          Đổi Mật Khẩu Tài Khoản
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="field-group">
            <label>Mật khẩu hiện tại</label>
            <input
              type="password"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="Nhập mật khẩu hiện tại..."
            />
          </div>
          <div className="field-group" style={{ marginTop: '12px' }}>
            <label>Mật khẩu mới (Tối thiểu 6 ký tự)</label>
            <input
              type="password"
              required
              minLength={6}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Nhập mật khẩu mới..."
            />
          </div>
          <div className="field-group" style={{ marginTop: '12px' }}>
            <label>Xác nhận mật khẩu mới</label>
            <input
              type="password"
              required
              minLength={6}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Nhập lại mật khẩu mới..."
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', marginTop: '22px' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={loading}>
              {loading ? 'Đang lưu...' : 'Lưu mật khẩu'}
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
