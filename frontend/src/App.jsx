// frontend/src/App.jsx
import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import Toast from './components/Toast';
import CameraModal from './components/CameraModal';
import EditModal from './components/EditModal';
import ChangePasswordModal from './components/ChangePasswordModal';
import ScanTab from './tabs/ScanTab';
import ResultsTab from './tabs/ResultsTab';
import StatisticsTab from './tabs/StatisticsTab';

import { getToken, removeToken, apiGetMe } from './services/api';

export default function App() {
  const [token, setTokenState] = useState(getToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('tab-scan'); // tab-scan | tab-results | tab-stats

  // Modals
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);

  // Toast
  const [toast, setToast] = useState({ message: '', isSuccess: true });
  const toastTimerRef = useRef(null);

  const showToast = (message, isSuccess = true) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ message, isSuccess });
    toastTimerRef.current = setTimeout(() => {
      setToast({ message: '', isSuccess: true });
    }, 3800);
  };

  useEffect(() => {
    // Tự động chuyển hướng từ 0.0.0.0 sang 127.0.0.1 để tránh lỗi Not Secure
    if (typeof window !== 'undefined') {
      if (window.location.hostname === '0.0.0.0') {
        window.location.replace(window.location.href.replace('//0.0.0.0', '//127.0.0.1'));
      }
      if (window.location.protocol === 'http:' && window.location.hostname.endsWith('hf.space')) {
        window.location.replace(window.location.href.replace('http:', 'https:'));
      }
    }

    const handleAuthExpired = () => {
      setTokenState('');
      setCurrentUser(null);
      showToast('⚠️ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', false);
    };
    window.addEventListener('auth-expired', handleAuthExpired);

    if (token) {
      apiGetMe()
        .then(async (res) => {
          if (res.ok) {
            const user = await res.json();
            setCurrentUser(user);
          } else {
            handleAuthExpired();
          }
        })
        .catch(() => {});
    }

    return () => {
      window.removeEventListener('auth-expired', handleAuthExpired);
    };
  }, [token]);

  const handleLoginSuccess = (user, accessToken) => {
    setTokenState(accessToken);
    setCurrentUser(user);
  };

  const handleLogout = () => {
    removeToken();
    setTokenState('');
    setCurrentUser(null);
    showToast('👋 Đã đăng xuất khỏi hệ thống!', true);
  };

  // If not logged in, show AuthModal screen
  if (!token) {
    return (
      <>
        <AuthModal onLoginSuccess={handleLoginSuccess} showToast={showToast} />
        <Toast toast={toast} />
      </>
    );
  }

  return (
    <div className="container">
      {/* NAVBAR */}
      <Navbar
        currentUser={currentUser}
        onOpenPasswordModal={() => setIsPasswordOpen(true)}
        onLogout={handleLogout}
      />

      {/* NAVIGATION TABS (FACEBOOK STYLE) */}
      <div className="tabs">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-scan' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-scan')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" rx="4" />
            <circle cx="12" cy="12" r="3.5" />
            <path d="M3 9h3M3 15h3M18 9h3M18 15h3" />
          </svg>
          1. Nhận Diện & Hiệu Chỉnh CCCD
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-results' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-results')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <line x1="10" y1="9" x2="8" y2="9" />
          </svg>
          2. Bảng Lưu Kết Quả (8 Trường)
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-stats')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          3. Thống Kê & Độ Đúng Của AI
        </button>
      </div>

      {/* TAB CONTENT PANELS */}
      {activeTab === 'tab-scan' && (
        <div id="tab-scan" className="tab-panel active">
          <ScanTab
            onOpenCamModal={() => setIsCameraOpen(true)}
            onSaveSuccess={() => {}}
            showToast={showToast}
          />
        </div>
      )}

      {activeTab === 'tab-results' && (
        <div id="tab-results" className="tab-panel active">
          <ResultsTab
            onEditRecord={(record) => setEditingRecord(record)}
            showToast={showToast}
          />
        </div>
      )}

      {activeTab === 'tab-stats' && (
        <div id="tab-stats" className="tab-panel active">
          <StatisticsTab showToast={showToast} />
        </div>
      )}

      {/* MODALS */}
      <CameraModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={(blob) => {
          if (ScanTab.processCameraCapture) {
            ScanTab.processCameraCapture(blob);
          }
        }}
        onNativeCaptureTrigger={() => {
          const nativeInput = document.getElementById('camera-native-input');
          if (nativeInput) nativeInput.click();
        }}
        showToast={showToast}
      />

      <EditModal
        isOpen={!!editingRecord}
        record={editingRecord}
        onClose={() => setEditingRecord(null)}
        onSaveSuccess={() => {}}
        onOpenInScanTab={(record) => {
          setActiveTab('tab-scan');
          showToast('✅ Đã tải thông tin vào Tab 1 để kiểm tra!', true);
        }}
        showToast={showToast}
      />

      <ChangePasswordModal
        isOpen={isPasswordOpen}
        onClose={() => setIsPasswordOpen(false)}
        showToast={showToast}
      />

      {/* TOAST NOTIFICATION */}
      <Toast toast={toast} />
    </div>
  );
}
