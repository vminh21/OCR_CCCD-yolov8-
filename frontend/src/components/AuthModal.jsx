// frontend/src/components/AuthModal.jsx
import React, { useState } from 'react';
import { apiLogin, apiRegister, setToken } from '../services/api';

export default function AuthModal({ onLoginSuccess, showToast }) {
  const [tab, setTab] = useState('login'); // 'login' | 'register'
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Login form
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [regFullName, setRegFullName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    if (!loginUsername.trim() || !loginPassword.trim()) {
      setErrorMsg('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    try {
      const res = await apiLogin(loginUsername.trim(), loginPassword.trim());
      const data = await res.json();
      if (res.ok && data.access_token) {
        setToken(data.access_token);
        showToast('✅ Đăng nhập thành công! Chào mừng bạn.', true);
        onLoginSuccess(data.user, data.access_token);
      } else {
        setErrorMsg(data.detail || 'Đăng nhập thất bại!');
      }
    } catch (err) {
      setErrorMsg('Lỗi kết nối server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = () => {
    setLoginUsername('minh_final');
    setLoginPassword('password123');
    setTimeout(() => {
      apiLogin('minh_final', 'password123')
        .then(async (res) => {
          const data = await res.json();
          if (res.ok && data.access_token) {
            setToken(data.access_token);
            showToast('✅ Đăng nhập nhanh tài khoản mẫu thành công!', true);
            onLoginSuccess(data.user, data.access_token);
          } else {
            setErrorMsg(data.detail || 'Đăng nhập mẫu thất bại!');
          }
        })
        .catch((err) => setErrorMsg('Lỗi kết nối: ' + err.message));
    }, 100);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await apiRegister(
        regFullName.trim(),
        regUsername.trim(),
        regEmail.trim(),
        regPassword.trim()
      );
      const data = await res.json();
      if (res.ok) {
        showToast('✅ Đăng ký thành công! Đang tự động đăng nhập...', true);
        // Auto login
        const loginRes = await apiLogin(regUsername.trim(), regPassword.trim());
        const loginData = await loginRes.json();
        if (loginRes.ok && loginData.access_token) {
          setToken(loginData.access_token);
          onLoginSuccess(loginData.user, loginData.access_token);
        } else {
          setTab('login');
          setLoginUsername(regUsername.trim());
        }
      } else {
        setErrorMsg(data.detail || 'Đăng ký tài khoản thất bại!');
      }
    } catch (err) {
      setErrorMsg('Lỗi kết nối: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="auth-screen" style={{ display: 'flex', minHeight: '88vh', alignItems: 'center', justifyContent: 'center', padding: '20px', position: 'relative' }}>
      <div style={{ background: '#ffffff', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '36px 32px', width: '100%', maxWidth: '440px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1), 0 8px 16px rgba(0, 0, 0, 0.1)', position: 'relative', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '22px' }}>
          <div style={{ width: '52px', height: '52px', margin: '0 auto 12px auto', borderRadius: '8px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', boxShadow: '0 2px 8px rgba(24, 119, 242, 0.3)' }}>
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '28px', height: '28px', color: 'white' }}>
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <circle cx="8" cy="10" r="2.5" />
              <line x1="13" y1="9" x2="19" y2="9" />
              <line x1="13" y1="13" x2="19" y2="13" />
              <line x1="5" y1="16" x2="11" y2="16" />
              <line x1="14" y1="16" x2="19" y2="16" />
            </svg>
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#050505', letterSpacing: '-0.4px' }}>
            CCCD <span style={{ color: 'var(--primary)' }}>OCR</span>
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 500 }}>
            Hệ Thống AI Định Danh • Nhóm 10 - 74DCTT24
          </p>
        </div>

        {/* TAB SWITCHER */}
        <div style={{ display: 'flex', background: '#e4e6eb', borderRadius: '6px', padding: '4px', marginBottom: '20px' }}>
          <button
            type="button"
            className="btn"
            style={{
              flex: 1,
              justifyContent: 'center',
              background: tab === 'login' ? '#ffffff' : 'transparent',
              color: tab === 'login' ? 'var(--primary)' : 'var(--text-muted)',
              boxShadow: tab === 'login' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none',
              fontWeight: 600,
            }}
            onClick={() => { setTab('login'); setErrorMsg(''); }}
          >
            Đăng Nhập
          </button>
          <button
            type="button"
            className="btn"
            style={{
              flex: 1,
              justifyContent: 'center',
              background: tab === 'register' ? '#ffffff' : 'transparent',
              color: tab === 'register' ? 'var(--primary)' : 'var(--text-muted)',
              boxShadow: tab === 'register' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none',
              fontWeight: 600,
            }}
            onClick={() => { setTab('register'); setErrorMsg(''); }}
          >
            Đăng Ký
          </button>
        </div>

        {/* ALERT BOX */}
        {errorMsg && (
          <div style={{ padding: '10px 14px', borderRadius: '6px', fontSize: '0.85rem', marginBottom: '16px', fontWeight: 600, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
            {errorMsg}
          </div>
        )}

        {/* LOGIN FORM */}
        {tab === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="field-group">
              <label>Tên đăng nhập (Username)</label>
              <input
                type="text"
                placeholder="VD: minh_final"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
            <div className="field-group" style={{ marginTop: '12px' }}>
              <label>Mật khẩu</label>
              <input
                type="password"
                placeholder="Nhập mật khẩu..."
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', marginTop: '20px', padding: '12px', fontSize: '0.98rem' }}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" y1="12" x2="3" y2="12" />
              </svg>
              {loading ? 'Đang xử lý...' : 'Đăng Nhập Hệ Thống'}
            </button>

            <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--divider)', textAlign: 'center' }}>
              <button
                type="button"
                className="btn btn-outline"
                style={{ width: '100%', fontSize: '0.85rem' }}
                onClick={handleQuickLogin}
              >
                <svg className="svg-icon" viewBox="0 0 24 24" style={{ color: '#f59e0b' }}>
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
                Đăng nhập nhanh tài khoản mẫu (minh_final)
              </button>
            </div>
          </form>
        )}

        {/* REGISTER FORM */}
        {tab === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="field-group">
              <label>Họ và tên hiển thị</label>
              <input
                type="text"
                placeholder="VD: Nguyễn Văn Minh"
                value={regFullName}
                onChange={(e) => setRegFullName(e.target.value)}
                required
              />
            </div>
            <div className="field-group" style={{ marginTop: '10px' }}>
              <label>Tên đăng nhập (Username)</label>
              <input
                type="text"
                placeholder="VD: minh123"
                value={regUsername}
                onChange={(e) => setRegUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
            <div className="field-group" style={{ marginTop: '10px' }}>
              <label>Địa chỉ Email</label>
              <input
                type="email"
                placeholder="VD: minh@example.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <div className="field-group" style={{ marginTop: '10px' }}>
              <label>Mật khẩu (Tối thiểu 6 ký tự)</label>
              <input
                type="password"
                placeholder="Nhập mật khẩu..."
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
            </div>
            <button
              type="submit"
              className="btn btn-success"
              disabled={loading}
              style={{ width: '100%', marginTop: '18px', padding: '11px', fontSize: '0.95rem' }}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <line x1="20" y1="8" x2="20" y2="14" />
                <line x1="23" y1="11" x2="17" y2="11" />
              </svg>
              {loading ? 'Đang tạo...' : 'Tạo Tài Khoản & Vào Hệ Thống'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
