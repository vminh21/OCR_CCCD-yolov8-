// frontend/src/components/CameraModal.jsx
import React, { useState, useEffect, useRef } from 'react';
import { apiProbeCamera } from '../services/api';

export default function CameraModal({ isOpen, onClose, onCapture, onNativeCaptureTrigger, showToast }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [videoDevices, setVideoDevices] = useState([]);
  const [currentDeviceId, setCurrentDeviceId] = useState(null);
  const [badgeText, setBadgeText] = useState('Đang khởi động Camera...');
  const [badgeColor, setBadgeColor] = useState('#38bdf8');
  const [isCapturing, setIsCapturing] = useState(false);

  const probeTimerRef = useRef(null);
  const isCapturingRef = useRef(false);
  const consecutiveHitsRef = useRef(0);
  const isInIframe = typeof window !== 'undefined' && window.self !== window.top;

  useEffect(() => {
    if (!isOpen) {
      cleanupCamera();
      return;
    }

    startCamera();

    const handleKeyDown = (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        captureCurrentFrame();
      } else if (e.code === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      cleanupCamera();
    };
  }, [isOpen, currentDeviceId]);

  const cleanupCamera = () => {
    if (probeTimerRef.current) {
      clearInterval(probeTimerRef.current);
      probeTimerRef.current = null;
    }
    if (stream) {
      try {
        stream.getTracks().forEach((t) => t.stop());
      } catch (e) {}
    }
    setStream(null);
  };

  const startCamera = async () => {
    setBadgeText('Đang khởi động Camera...');
    setBadgeColor('#38bdf8');
    isCapturingRef.current = false;
    consecutiveHitsRef.current = 0;

    try {
      if (!window.isSecureContext && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        throw new Error('Trình duyệt khóa Camera trên kết nối không bảo mật! Vui lòng truy cập qua HTTPS.');
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (isInIframe) {
          throw new Error('Khung nhúng Hugging Face Hub chặn quyền Camera! Vui lòng bấm "Mở Tab Riêng" hoặc "Chụp Bằng Máy".');
        }
        throw new Error('Trình duyệt không hỗ trợ Camera trực tiếp!');
      }

      const constraints = {
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };

      if (currentDeviceId) {
        constraints.video.deviceId = { exact: currentDeviceId };
      }

      let mediaStream = null;
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      } catch (err1) {
        // Fallback video: true
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play().catch(() => {});
      }

      // Check available camera devices
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const vDevs = devices.filter((d) => d.kind === 'videoinput' && d.deviceId);
        setVideoDevices(vDevs);
      } catch (e) {}

      // Start probe loop
      startProbeLoop();
    } catch (err) {
      console.error('Camera error:', err);
      let friendlyMsg = 'Không thể mở Camera: ' + (err.message || err.name);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError' || err.name === 'SecurityError') {
        if (isInIframe) {
          friendlyMsg = '⚠️ Camera bị chặn do đang xem trong khung nhúng Hugging Face Hub! Vui lòng bấm "Mở Tab Riêng" ở thông báo bên trên.';
        } else {
          friendlyMsg = '⚠️ Bạn chưa cho phép trình duyệt dùng Camera! Vui lòng bấm vào biểu tượng 🔒 hoặc Camera trên thanh URL rồi chọn "Cho phép" (Allow).';
        }
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        friendlyMsg = '⚠️ Camera đang bị ứng dụng khác (Zoom, FaceTime, Meet) chiếm dụng. Vui lòng tắt các ứng dụng đó rồi thử lại!';
      }
      showToast(friendlyMsg, false);
      setBadgeText(isInIframe ? 'Bị chặn bởi khung Hugging Face' : 'Lỗi Camera');
      setBadgeColor('#ef4444');
    }
  };

  const startProbeLoop = () => {
    if (probeTimerRef.current) clearInterval(probeTimerRef.current);
    probeTimerRef.current = setInterval(async () => {
      if (isCapturingRef.current || !videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      if (video.readyState < 2 || video.videoWidth === 0) return;

      const canvas = canvasRef.current;
      canvas.width = 640;
      canvas.height = 360;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob || isCapturingRef.current) return;
        try {
          const res = await apiProbeCamera(blob);
          if (!res.ok) return;
          const data = await res.json();
          handleProbeFeedback(data);
        } catch (e) {}
      }, 'image/jpeg', 0.65);
    }, 450);
  };

  const handleProbeFeedback = (data) => {
    if (isCapturingRef.current) return;

    setBadgeText(data.message || 'Căn thẻ vào khung...');
    if (data.color === 'green') {
      setBadgeColor('#22c55e');
    } else if (data.color === 'yellow') {
      setBadgeColor('#f59e0b');
    } else {
      setBadgeColor('#ef4444');
    }

    // Auto capture logic
    if (data.detected && data.auto_capture) {
      consecutiveHitsRef.current += 1;
      if (consecutiveHitsRef.current >= 3) {
        captureCurrentFrame();
      }
    } else {
      consecutiveHitsRef.current = 0;
    }
  };

  const captureCurrentFrame = () => {
    if (isCapturingRef.current || !videoRef.current || !canvasRef.current) return;
    isCapturingRef.current = true;
    setIsCapturing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        onCapture(blob);
        onClose();
      }
      setIsCapturing(false);
      isCapturingRef.current = false;
    }, 'image/jpeg', 0.95);
  };

  const handleSwitchCamera = () => {
    if (videoDevices.length < 2) return;
    const currentIndex = videoDevices.findIndex((d) => d.deviceId === currentDeviceId);
    const nextIndex = (currentIndex + 1) % videoDevices.length;
    setCurrentDeviceId(videoDevices[nextIndex].deviceId);
  };

  if (!isOpen) return null;

  return (
    <div id="modal-camera" className="modal active">
      <div className="modal-content" style={{ maxWidth: '720px', width: '95%', padding: '20px', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '34px', height: '34px', borderRadius: '6px', background: 'var(--primary-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '18px', height: '18px' }}>
                <path d="M23 7l-7 5 7 5V7z" />
                <rect x="1" y="5" width="15" height="14" rx="2" />
              </svg>
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Quét & Nhận Diện CCCD Bằng Camera
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0 0', fontWeight: 500 }}>
                Căn chỉnh thẻ vào khung • Tự động chụp hoặc nhấn phím <strong style={{ color: 'var(--primary)' }}>Space</strong> / nút Chụp
              </p>
            </div>
          </div>
          <button type="button" className="btn btn-outline" style={{ padding: '4px 10px', borderRadius: '4px' }} onClick={onClose}>
            ✕
          </button>
        </div>

        {/* CẢNH BÁO CHO TRƯỜNG HỢP MỞ QUA IFRAME HUGGING FACE */}
        {isInIframe && (
          <div style={{ display: 'flex', marginBottom: '12px', padding: '10px 14px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '6px', fontSize: '0.85rem', color: '#1e40af', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
            <span>💡 <strong>Lưu ý:</strong> Khung nhúng Hugging Face Hub có thể chặn Camera. Bạn hãy mở trên Tab riêng:</span>
            <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
              <button
                type="button"
                className="btn btn-outline"
                style={{ padding: '5px 10px', fontSize: '0.8rem', background: '#fff' }}
                onClick={() => {
                  onClose();
                  onNativeCaptureTrigger();
                }}
              >
                Chụp Bằng Máy
              </button>
              <a
                href="https://vminh21-ccccd-ocr.hf.space"
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
                style={{ padding: '5px 12px', fontSize: '0.8rem', textDecoration: 'none', whiteSpace: 'nowrap' }}
              >
                Mở Tab Riêng
              </a>
            </div>
          </div>
        )}

        {/* KHUNG CAMERA VIEWPORT */}
        <div style={{ position: 'relative', width: '100%', aspectRatio: '16/9', background: '#000', borderRadius: '8px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-color)', boxShadow: 'inset 0 0 24px rgba(0,0,0,0.85)' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <canvas ref={overlayCanvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 8 }} />

          {/* LỚP PHỦ CĂN THẺ TỶ LỆ CHUẨN 1.586 */}
          <div style={{ position: 'absolute', width: '75%', maxWidth: '480px', aspectRatio: '1.586', border: '2px dashed rgba(255, 255, 255, 0.7)', borderRadius: '6px', boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.52)', pointerEvents: 'none', transition: 'all 0.25s ease' }}>
            <div style={{ position: 'absolute', top: '-3px', left: '-3px', width: '24px', height: '24px', borderTop: '3px solid #38bdf8', borderLeft: '3px solid #38bdf8', borderTopLeftRadius: '6px' }} />
            <div style={{ position: 'absolute', top: '-3px', right: '-3px', width: '24px', height: '24px', borderTop: '3px solid #38bdf8', borderRight: '3px solid #38bdf8', borderTopRightRadius: '6px' }} />
            <div style={{ position: 'absolute', bottom: '-3px', left: '-3px', width: '24px', height: '24px', borderBottom: '3px solid #38bdf8', borderLeft: '3px solid #38bdf8', borderBottomLeftRadius: '6px' }} />
            <div style={{ position: 'absolute', bottom: '-3px', right: '-3px', width: '24px', height: '24px', borderBottom: '3px solid #38bdf8', borderRight: '3px solid #38bdf8', borderBottomRightRadius: '6px' }} />

            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, textShadow: '0 1px 4px rgba(0,0,0,0.9)', pointerEvents: 'none' }}>
              <span>CĂN MẶT TRƯỚC CCCD VÀO ĐÂY</span>
            </div>

            <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
              <div style={{ width: '100%', height: '2px', background: 'linear-gradient(90deg, transparent, #38bdf8, transparent)', boxShadow: '0 0 10px #38bdf8', animation: 'scanMove 2.2s ease-in-out infinite' }} />
            </div>
          </div>

          {/* STATUS PILL */}
          <div style={{ position: 'absolute', bottom: '16px', zIndex: 12, padding: '7px 18px', background: 'rgba(15, 23, 42, 0.88)', backdropFilter: 'blur(8px)', borderRadius: '999px', border: '1px solid rgba(255, 255, 255, 0.25)', color: '#ffffff', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 16px rgba(0,0,0,0.4)' }}>
            <span style={{ width: '9px', height: '9px', borderRadius: '50%', background: badgeColor, display: 'inline-block' }} />
            <span>{badgeText}</span>
          </div>
        </div>

        {/* ACTION BUTTONS */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
          <div>
            {videoDevices.length > 1 && (
              <button type="button" className="btn btn-outline" style={{ padding: '8px 14px', fontSize: '0.85rem' }} onClick={handleSwitchCamera}>
                <svg className="svg-icon" viewBox="0 0 24 24">
                  <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
                </svg>
                Đổi Camera
              </button>
            )}
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="button" className="btn btn-outline" style={{ padding: '10px 18px' }} onClick={onClose}>
              Đóng
            </button>
            <button
              type="button"
              className="btn btn-primary"
              style={{ padding: '10px 24px', fontWeight: 700 }}
              disabled={isCapturing}
              onClick={captureCurrentFrame}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="3" />
                <path d="M19 4h-3.5L14 2H10L8.5 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z" />
              </svg>
              {isCapturing ? 'Đang chụp...' : 'Chụp Ảnh Ngay (Space)'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
