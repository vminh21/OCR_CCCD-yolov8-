// frontend/src/components/Navbar.jsx
import React from 'react';

export default function Navbar({ currentUser, onOpenProfile, onOpenPasswordModal, onLogout }) {
  return (
    <header>
      <div className="logo-area">
        <div className="logo-icon-box">
          <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '22px', height: '22px', color: 'white' }}>
            <rect x="2" y="4" width="20" height="16" rx="3" />
            <circle cx="8" cy="10" r="2.5" />
            <line x1="13" y1="9" x2="19" y2="9" />
            <line x1="13" y1="13" x2="19" y2="13" />
            <line x1="5" y1="16" x2="11" y2="16" />
            <line x1="14" y1="16" x2="19" y2="16" />
          </svg>
        </div>
        <div className="logo-title-group">
          <h1>
            CCCD <span style={{ color: 'var(--primary)' }}>OCR</span>
          </h1>
          <p>YOLOv8 + VietOCR Transformer • Nhóm 10 - 74DCTT24</p>
        </div>
      </div>

      <div className="user-nav">
        <div
          className="user-badge"
          id="user-display"
          onClick={onOpenProfile}
          style={{ cursor: 'pointer' }}
          title="Bấm để mở Quản Lý Tài Khoản"
        >
          <div className="user-avatar-circle">
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '14px', height: '14px' }}>
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <span id="username-text">
            {currentUser?.full_name || currentUser?.username || 'Người dùng'}
          </span>
          <span id="user-sub" style={{ color: 'var(--text-muted)', fontSize: '0.78rem', fontWeight: 'normal', marginLeft: '2px' }}>
            {currentUser?.username ? `(@${currentUser.username})` : ''}
          </span>
        </div>

        <button type="button" className="btn btn-outline" onClick={onOpenPasswordModal}>
          <svg className="svg-icon" viewBox="0 0 24 24" style={{ color: '#6366f1' }}>
            <circle cx="7.5" cy="15.5" r="4.5" />
            <path d="m21 3-9.5 9.5" />
            <path d="m15.5 7.5 3 3" />
            <path d="m18.5 4.5 2 2" />
          </svg>
          Đổi mật khẩu
        </button>

        <button type="button" className="btn btn-danger" onClick={onLogout}>
          <svg className="svg-icon" viewBox="0 0 24 24">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Đăng xuất
        </button>
      </div>
    </header>
  );
}
