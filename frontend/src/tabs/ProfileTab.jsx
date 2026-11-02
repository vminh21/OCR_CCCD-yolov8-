// frontend/src/tabs/ProfileTab.jsx
import React, { useState, useEffect } from 'react';
import {
  apiChangePassword,
  getUserAIKey,
  setUserAIKey,
  getUserAIProvider,
  removeUserAIKey,
  apiGetEvaluateStatus,
  apiTestEvaluateKey
} from '../services/api';

export default function ProfileTab({ currentUser, onLogout, showToast }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // AI Key state
  const [userKey, setUserKeyState] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [showKey, setShowKey] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [isTestingKey, setIsTestingKey] = useState(false);
  const [keyTestMessage, setKeyTestMessage] = useState(null);

  useEffect(() => {
    setUserKeyState(getUserAIKey());
    setProvider(getUserAIProvider());
    // Lấy trạng thái hệ thống từ backend
    apiGetEvaluateStatus()
      .then((res) => res.json())
      .then((data) => setSystemStatus(data))
      .catch(() => {});
  }, []);


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

  const handleSaveKey = () => {
    if (!userKey.trim()) {
      removeUserAIKey();
      setUserKeyState('');
      if (showToast) showToast('Đã xóa key cá nhân, hệ thống sẽ dùng key mặc định từ .env', true);
      return;
    }
    setUserAIKey(userKey.trim(), provider);
    if (showToast) showToast('✅ Đã lưu API Key cá nhân vào trình duyệt thành công!', true);
  };

  const handleClearKey = () => {
    removeUserAIKey();
    setUserKeyState('');
    setKeyTestMessage(null);
    if (showToast) showToast('Đã xóa key cá nhân. Quay lại dùng key mặc định hệ thống (.env).', true);
  };

  const handleTestKey = async () => {
    setIsTestingKey(true);
    setKeyTestMessage(null);
    try {
      const res = await apiTestEvaluateKey(userKey.trim(), provider);
      const data = await res.json();
      setKeyTestMessage(data);
      if (data.valid) {
        if (showToast) showToast('✅ ' + data.message, true);
      } else {
        if (showToast) showToast('❌ ' + data.message, false);
      }
    } catch (err) {
      const errMsg = 'Lỗi kết nối kiểm tra key: ' + err.message;
      setKeyTestMessage({ valid: false, message: errMsg });
      if (showToast) showToast(errMsg, false);
    } finally {
      setIsTestingKey(false);
    }
  };

  const hasSystemKey = systemStatus?.system_key_configured;
  const isUsingUserKey = !!userKey.trim();

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

      {/* KHUNG 3: CẤU HÌNH API KEY THẨM ĐỊNH (AI ORACLE GROUND TRUTH) */}
      <div className="card" style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#ecfdf5', color: '#059669' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
              </svg>
            </span>
            <span>Cấu Hình API Key Thẩm Định Tự Động (AI Oracle)</span>
          </span>
          {isUsingUserKey ? (
            <span className="badge badge-info" style={{ background: '#e0f2fe', color: '#0284c7' }}>
              🔑 Đang dùng Key cá nhân
            </span>
          ) : hasSystemKey ? (
            <span className="badge badge-success" style={{ background: '#dcfce7', color: '#16a34a' }}>
              🟢 Đang dùng Key hệ thống (.env)
            </span>
          ) : (
            <span className="badge badge-warning" style={{ background: '#fef3c7', color: '#d97706' }}>
              ⚪ Chưa có Key mặc định
            </span>
          )}
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
          {/* CHỌN PROVIDER */}
          <div className="field-group">
            <label style={{ fontWeight: 600, color: '#334155', display: 'flex', alignItems: 'center', gap: '6px' }}>
              Mô hình Vision AI thẩm định:
            </label>
            <div style={{ display: 'flex', gap: '20px', marginTop: '6px', flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 500 }}>
                <input
                  type="radio"
                  name="ai_provider"
                  value="gemini"
                  checked={provider === 'gemini'}
                  onChange={(e) => setProvider(e.target.value)}
                />
                <span>Google Gemini Flash (Miễn phí - Khuyên dùng)</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 500 }}>
                <input
                  type="radio"
                  name="ai_provider"
                  value="openai"
                  checked={provider === 'openai'}
                  onChange={(e) => setProvider(e.target.value)}
                />
                <span>OpenAI (GPT-4o-mini Vision)</span>
              </label>
            </div>
          </div>

          {/* NHẬP KEY */}
          <div className="field-group">
            <label style={{ fontWeight: 600, color: '#334155', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>
                {isUsingUserKey ? '🔑 API Key Cá Nhân Đang Lưu Trên Trình Duyệt:' : '🔑 Nhập API Key Cá Nhân Mới (Tùy chọn):'}
              </span>
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
              >
                {showKey ? '🙈 Ẩn Key' : '👁️ Hiện Key'}
              </button>
            </label>
            <input
              type={showKey ? 'text' : 'password'}
              value={userKey}
              onChange={(e) => setUserKeyState(e.target.value)}
              placeholder={
                provider === 'gemini'
                  ? 'Dán key Google Gemini vào đây...'
                  : 'Dán key OpenAI vào đây...'
              }
              style={{ fontFamily: 'monospace', letterSpacing: showKey ? 'normal' : '2px', padding: '12px' }}
            />
          </div>

          {/* TEST MESSAGE NẾU CÓ */}
          {keyTestMessage && (
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '8px',
                fontSize: '0.88rem',
                background: keyTestMessage.valid ? '#ecfdf5' : '#fef2f2',
                border: `1px solid ${keyTestMessage.valid ? '#a7f3d0' : '#fecaca'}`,
                color: keyTestMessage.valid ? '#065f46' : '#991b1b',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}
            >
              <span style={{ fontSize: '1.2rem' }}>{keyTestMessage.valid ? '✅' : '❌'}</span>
              <div>
                <div><strong>{keyTestMessage.message}</strong></div>
                {keyTestMessage.model && (
                  <div style={{ fontSize: '0.8rem', opacity: 0.9, marginTop: '2px' }}>
                    Mô hình phản hồi: <code>{keyTestMessage.model}</code> | Nguồn key: <code>{keyTestMessage.source === 'user' ? 'Cá nhân (Trình duyệt)' : 'Mặc định (.env)'}</code>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* HÀNG NÚT BẤM */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '6px' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSaveKey}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <span>💾 Lưu Key Cá Nhân</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleTestKey}
              disabled={isTestingKey}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <span>{isTestingKey ? '⏳ Đang kiểm tra kết nối...' : `⚡ Kiểm Tra Kết Nối (${userKey.trim() ? 'Key Vừa Nhập' : 'Key .env Mặc Định'})`}</span>
            </button>

            {isUsingUserKey && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleClearKey}
                style={{ color: '#ef4444', borderColor: '#fca5a5', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <span>🔄 Xóa Key Cá Nhân (Quay Lại Dùng .env)</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

