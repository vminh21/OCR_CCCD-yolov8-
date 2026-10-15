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
import AIAccuracyTab from './tabs/AIAccuracyTab';
import ProfileTab from './tabs/ProfileTab';

import { getToken, removeToken, apiGetMe } from './services/api';

const TAB_MAP = {
  'tab-scan': '#scan',
  'tab-results': '#results',
  'tab-stats': '#stats',
  'tab-ai-accuracy': '#ai-accuracy',
  'tab-profile': '#profile',
};

const HASH_MAP = {
  '#scan': 'tab-scan',
  '#results': 'tab-results',
  '#stats': 'tab-stats',
  '#ai-accuracy': 'tab-ai-accuracy',
  '#profile': 'tab-profile',
};

const getTabFromHash = () => {
  if (typeof window !== 'undefined') {
    const hash = window.location.hash;
    if (HASH_MAP[hash]) return HASH_MAP[hash];
  }
  return 'tab-scan';
};

export default function App() {
  const [token, setTokenState] = useState(getToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState(getTabFromHash);

  // Modals
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);

  // Loaded record for Tab 1 scanning/editing
  const [loadedRecordForScan, setLoadedRecordForScan] = useState(null);

  // Điều hướng Tab kèm cập nhật Browser History (hỗ trợ nút Back / Forward & Reload trang)
  const navigateToTab = (tabId, replace = false) => {
    const targetHash = TAB_MAP[tabId] || '#scan';
    if (typeof window !== 'undefined') {
      if (window.location.hash !== targetHash) {
        if (replace) {
          window.history.replaceState(null, '', targetHash);
        } else {
          window.history.pushState(null, '', targetHash);
        }
      }
    }
    setActiveTab(tabId);
  };

  const handleLoadRecordToScan = (record) => {
    setLoadedRecordForScan(record);
    navigateToTab('tab-scan');
    showToast(`✅ Đã nạp hồ sơ #${record.id} (${record.full_name || ''}) vào Form Tab 1!`, true);
  };

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

  // Lắng nghe sự kiện Back / Forward của trình duyệt (popstate & hashchange)
  useEffect(() => {
    const handleLocationChange = () => {
      const hash = window.location.hash;
      const tab = HASH_MAP[hash] || 'tab-scan';
      setActiveTab(tab);
      // Khi người dùng bấm Back/Forward, tự động đóng các modal đang mở
      setEditingRecord(null);
      setIsCameraOpen(false);
      setIsPasswordOpen(false);
    };

    if (typeof window !== 'undefined') {
      if (!window.location.hash || !HASH_MAP[window.location.hash]) {
        const defaultHash = TAB_MAP[activeTab] || '#scan';
        window.history.replaceState(null, '', defaultHash);
      }
    }

    window.addEventListener('popstate', handleLocationChange);
    window.addEventListener('hashchange', handleLocationChange);

    return () => {
      window.removeEventListener('popstate', handleLocationChange);
      window.removeEventListener('hashchange', handleLocationChange);
    };
  }, []);

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
        onOpenProfile={() => navigateToTab('tab-profile')}
        onOpenPasswordModal={() => setIsPasswordOpen(true)}
        onLogout={handleLogout}
      />

      {/* NAVIGATION TABS (FACEBOOK STYLE) */}
      <div className="tabs">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-scan' ? 'active' : ''}`}
          onClick={() => navigateToTab('tab-scan')}
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
          onClick={() => navigateToTab('tab-results')}
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
          onClick={() => navigateToTab('tab-stats')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          3. Thống Kê & Nhân Khẩu Học
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-ai-accuracy' ? 'active' : ''}`}
          onClick={() => navigateToTab('tab-ai-accuracy')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          4. Đánh Giá Độ Đúng Của AI
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'tab-profile' ? 'active' : ''}`}
          onClick={() => navigateToTab('tab-profile')}
        >
          <svg className="svg-icon" viewBox="0 0 24 24">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          5. Quản Lý Tài Khoản
        </button>
      </div>

      {/* TAB CONTENT PANELS */}
      {activeTab === 'tab-scan' && (
        <div id="tab-scan" className="tab-panel active">
          <ScanTab
            onOpenCamModal={() => setIsCameraOpen(true)}
            onSaveSuccess={() => {}}
            loadedRecord={loadedRecordForScan}
            onClearLoadedRecord={() => setLoadedRecordForScan(null)}
            showToast={showToast}
          />
        </div>
      )}

      {activeTab === 'tab-results' && (
        <div id="tab-results" className="tab-panel active">
          <ResultsTab
            onEditRecord={(record) => setEditingRecord(record)}
            onLoadToScan={handleLoadRecordToScan}
            showToast={showToast}
          />
        </div>
      )}

      {activeTab === 'tab-stats' && (
        <div id="tab-stats" className="tab-panel active">
          <StatisticsTab showToast={showToast} />
        </div>
      )}

      {activeTab === 'tab-ai-accuracy' && (
        <div id="tab-ai-accuracy" className="tab-panel active">
          <AIAccuracyTab showToast={showToast} />
        </div>
      )}

      {activeTab === 'tab-profile' && (
        <div id="tab-profile" className="tab-panel active">
          <ProfileTab
            currentUser={currentUser}
            onLogout={handleLogout}
            showToast={showToast}
          />
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
        onOpenInScanTab={handleLoadRecordToScan}
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
