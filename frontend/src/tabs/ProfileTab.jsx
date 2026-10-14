// frontend/src/tabs/ProfileTab.jsx
import React, { useState } from 'react';
import { apiChangePassword } from '../services/api';

export default function ProfileTab({ currentUser, onLogout, showToast }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formattedCreatedDate = currentUser?.created_at
    ? new Date(currentUser.created_at).toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    : '---';

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (!oldPassword) {
      showToast('Vui lòng nhập mật khẩu hiện tại!', false);
      return;
    }

    if (newPassword.length < 6) {
      showToast('Mật khẩu mới phải có tối thiểu 6 ký tự!', false);
      return;
    }

    if (newPassword !== confirmPassword) {
      showToast('Mật khẩu mới và xác nhận mật khẩu không khớp!', false);
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await apiChangePassword(oldPassword, newPassword);
      const data = await res.json();
      if (res.ok) {
        showToast('✅ Đổi mật khẩu thành công!', true);
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        showToast(data.detail || 'Đổi mật khẩu thất bại!', false);
      }
    } catch (err) {
      showToast('Lỗi kết nối: ' + err.message, false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="profile-grid">
      {/* KHUNG 1: THÔNG TIN TÀI KHOẢN */}
      <div className="card">
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </span>
            <span>Thông Tin Tài Khoản</span>
          </span>
          <span className="badge badge-success">Đang hoạt động</span>
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Tên đăng nhập (Username):
            </label>
            <input
              type="text"
              readOnly
              value={currentUser?.username || ''}
              style={{ background: '#f8fafc', color: 'var(--text-muted)', fontWeight: 600 }}
            />
          </div>

          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Họ và tên người dùng:
            </label>
            <input
              type="text"
              readOnly
              value={currentUser?.full_name || currentUser?.username || ''}
              style={{ background: '#f8fafc', color: 'var(--text-main)', fontWeight: 700 }}
            />
          </div>

          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
              Email liên hệ:
            </label>
            <input
              type="text"
              readOnly
              value={currentUser?.email || ''}
              style={{ background: '#f8fafc', color: 'var(--text-main)' }}
            />
          </div>

          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              Thời điểm tạo tài khoản:
            </label>
            <input
              type="text"
              readOnly
              value={formattedCreatedDate}
              style={{ background: '#f8fafc', color: 'var(--text-muted)' }}
            />
          </div>

          <div style={{ marginTop: '12px', display: 'flex', gap: '10px' }}>
            <button
              type="button"
              className="btn btn-danger"
              style={{ width: '100%', padding: '12px' }}
              onClick={onLogout}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Đăng Xuất Khỏi Hệ Thống
            </button>
          </div>
        </div>
      </div>

      {/* KHUNG 2: ĐỔI MẬT KHẨU */}
      <div className="card">
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#fef2f2', color: '#dc2626' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </span>
            <span>Đổi Mật Khẩu Đăng Nhập</span>
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Bảo mật tài khoản
          </span>
        </h2>

        <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <circle cx="7.5" cy="15.5" r="4.5" />
                <path d="m21 3-9.5 9.5" />
                <path d="m15.5 7.5 3 3" />
                <path d="m18.5 4.5 2 2" />
              </svg>
              Mật khẩu hiện tại:
            </label>
            <input
              type="password"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="Nhập mật khẩu hiện tại..."
            />
          </div>

          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              Mật khẩu mới:
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Tối thiểu 6 ký tự..."
            />
          </div>

          <div className="field-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '15px', height: '15px', color: '#64748b' }}>
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              Xác nhận mật khẩu mới:
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Nhập lại mật khẩu mới..."
            />
          </div>

          <div style={{ marginTop: '12px' }}>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px 26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              disabled={isSubmitting}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                <polyline points="17 21 17 13 7 13 7 21" />
                <polyline points="7 3 7 8 15 8" />
              </svg>
              {isSubmitting ? 'Đang cập nhật...' : 'Cập Nhật Mật Khẩu'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
