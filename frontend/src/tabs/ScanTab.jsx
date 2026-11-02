// frontend/src/tabs/ScanTab.jsx
import React, { useState, useRef, useEffect } from 'react';
import {
  apiPredictImage,
  apiUpdateResult,
  apiEvaluateOnDemand,
  getUserAIKey,
  setUserAIKey,
  apiTestEvaluateKey,
  apiGetEvaluateStatus
} from '../services/api';
import AIComparisonModal from '../components/AIComparisonModal';

export default function ScanTab({ onOpenCamModal, onSaveSuccess, loadedRecord, onClearLoadedRecord, showToast }) {
  const [file, setFile] = useState(null);
  const [previewSrc, setPreviewSrc] = useState('');
  const [status, setStatus] = useState({ state: 'ready', message: '' }); // ready | loading | success | error
  const [sourceBadge, setSourceBadge] = useState('Sẵn sàng');
  const [sourceType, setSourceType] = useState('IMAGE'); // IMAGE | WEBCAM | VIDEO
  const [saving, setSaving] = useState(false);

  // AI Evaluation state
  const [evaluateWithAi, setEvaluateWithAi] = useState(true);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [showEvalModal, setShowEvalModal] = useState(false);
  const [isEvaluatingOnDemand, setIsEvaluatingOnDemand] = useState(false);

  // Quick API Key state
  const [showKeyBox, setShowKeyBox] = useState(false);
  const [quickKey, setQuickKey] = useState('');
  const [isTestingQuickKey, setIsTestingQuickKey] = useState(false);
  const [quickKeyMsg, setQuickKeyMsg] = useState(null);
  const [systemKeyConfigured, setSystemKeyConfigured] = useState(false);

  const [currentScanId, setCurrentScanId] = useState(null);
  const [currentResultId, setCurrentResultId] = useState(null);

  const [formData, setFormData] = useState({
    so_cccd: '',
    ho_ten: '',
    ngay_sinh: '',
    gioi_tinh: '',
    quoc_tich: 'Việt Nam',
    que_quan: '',
    noi_ctru: '',
    ngay_het_han: '',
  });


  const fileInputRef = useRef(null);
  const nativeCameraInputRef = useRef(null);
  const dropzoneRef = useRef(null);
  const evalSectionRef = useRef(null);

  const handleOpenEvalDetail = () => {
    setShowEvalModal(true);
    setTimeout(() => {
      if (evalSectionRef.current) {
        evalSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 60);
  };

  // Lắng nghe khi người dùng bấm "Tải vào Form Tab 1 để quét lại" từ Bảng kết quả (Tab 2)
  React.useEffect(() => {
    if (loadedRecord) {
      setFormData({
        so_cccd: loadedRecord.id_number || '',
        ho_ten: loadedRecord.full_name || '',
        ngay_sinh: loadedRecord.dob || '',
        gioi_tinh: loadedRecord.gender || '',
        quoc_tich: loadedRecord.nationality || 'Việt Nam',
        que_quan: loadedRecord.origin_location || '',
        noi_ctru: loadedRecord.residence || '',
        ngay_het_han: loadedRecord.expiry_date || '',
      });
      setCurrentResultId(loadedRecord.id);
      setCurrentScanId(loadedRecord.history_id || loadedRecord.id);
      const imgPath = loadedRecord.crop_image_path || '/media/cccd_fields_visualization.jpg';
      setPreviewSrc(imgPath + '?t=' + Date.now());
      setSourceBadge('📂 Hồ sơ #' + loadedRecord.id);
      setStatus({
        state: 'ready',
        message: `ℹ️ Đã nạp dữ liệu hồ sơ #${loadedRecord.id} (${loadedRecord.full_name || ''}) vào Form. Bạn có thể chỉnh sửa trực tiếp và bấm 'Xác Nhận & Lưu' hoặc chọn file mới để quét lại.`,
      });
      if (onClearLoadedRecord) onClearLoadedRecord();
    }
  }, [loadedRecord]);

  useEffect(() => {
    const k = getUserAIKey();
    if (k) setQuickKey(k);
    apiGetEvaluateStatus()
      .then((res) => res.json())
      .then((data) => setSystemKeyConfigured(!!data?.system_key_configured))
      .catch(() => {});
  }, []);

  const handleSaveQuickKey = () => {
    if (!quickKey.trim()) {
      setUserAIKey('', 'gemini');
      if (showToast) showToast('Đã xóa key cá nhân, hệ thống sẽ dùng key .env', true);
      setQuickKeyMsg({ valid: true, message: 'Đã chuyển về dùng key mặc định từ file .env' });
      return;
    }
    setUserAIKey(quickKey.trim(), 'gemini');
    if (showToast) showToast('✅ Đã lưu API Key cá nhân thành công!', true);
    setQuickKeyMsg({ valid: true, message: 'Đã lưu key cá nhân vào trình duyệt!' });
  };

  const handleTestQuickKey = async () => {
    setIsTestingQuickKey(true);
    setQuickKeyMsg(null);
    try {
      const res = await apiTestEvaluateKey(quickKey.trim(), 'gemini');
      const data = await res.json();
      setQuickKeyMsg(data);
      if (data.valid) {
        if (showToast) showToast('✅ ' + data.message, true);
      } else {
        if (showToast) showToast('❌ ' + data.message, false);
      }
    } catch (err) {
      setQuickKeyMsg({ valid: false, message: 'Lỗi: ' + err.message });
    } finally {
      setIsTestingQuickKey(false);
    }
  };

  const handleFieldChange = (field, val) => {
    setFormData((prev) => ({ ...prev, [field]: val }));
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    const isVideo = (selectedFile.type && selectedFile.type.startsWith('video/')) || /\.(mp4|avi|mov|mkv|webm)$/i.test(selectedFile.name || '');
    processFile(selectedFile, false, isVideo ? 'VIDEO' : 'IMAGE');
  };

  const processFile = async (fileOrBlob, isCamera = false, sourceOverride = null) => {
    let sourceVal = sourceOverride;
    if (!sourceVal) {
      if (isCamera) sourceVal = 'WEBCAM';
      else {
        const isVideo = (fileOrBlob.type && fileOrBlob.type.startsWith('video/')) || /\.(mp4|avi|mov|mkv|webm)$/i.test(fileOrBlob.name || '');
        sourceVal = isVideo ? 'VIDEO' : 'IMAGE';
      }
    }
    setSourceType(sourceVal);
    setFile(fileOrBlob);

    if (sourceVal === 'WEBCAM') {
      setSourceBadge('📸 Webcam');
    } else if (sourceVal === 'VIDEO') {
      setSourceBadge('🎥 Video');
    } else {
      setSourceBadge('🖼️ Ảnh tải lên');
    }

    if (!fileOrBlob.type || !fileOrBlob.type.startsWith('video/')) {
      setPreviewSrc(URL.createObjectURL(fileOrBlob));
    }

    setStatus({
      state: 'loading',
      message: sourceVal === 'WEBCAM'
        ? '⏳ [Webcam] Đang xoay nắn 360°, bóc tách 8 vùng & nhận diện VietOCR...'
        : (sourceVal === 'VIDEO'
          ? '⏳ [Video] Đang trích xuất frame, bóc tách 8 vùng & nhận diện VietOCR...'
          : '⏳ Đang xoay nắn 360°, bóc tách 8 vùng & nhận diện VietOCR...'),
    });

    try {
      const res = await apiPredictImage(fileOrBlob, sourceVal, evaluateWithAi);
      const data = await res.json();

      if (!res.ok || data.error) {
        const errText = data.error || 'Nhận diện thất bại!';
        setStatus({ state: 'error', message: '❌ ' + errText });
        showToast('❌ ' + errText, false);
        resetFieldsOnly();
        return;
      }

      if (data.visualization_base64) {
        setPreviewSrc(data.visualization_base64);
      }

      setFormData({
        so_cccd: data.so_cccd || '',
        ho_ten: data.ho_ten || '',
        ngay_sinh: data.ngay_sinh || '',
        gioi_tinh: data.gioi_tinh || '',
        quoc_tich: data.quoc_tich || 'Việt Nam',
        que_quan: data.que_quan || '',
        noi_ctru: data.noi_ctru || '',
        ngay_het_han: data.ngay_het_han || '',
      });

      setCurrentScanId(data.scan_id);
      setCurrentResultId(data.result_id);

      if (data.ai_evaluation) {
        setEvaluationResult(data.ai_evaluation);
      } else {
        setEvaluationResult(null);
      }

      setStatus({
        state: 'success',
        message: '✅ Nhận diện thành công! Đã khoanh vùng 8 trường và lưu vào CSDL.',
      });
      showToast('✅ Đã nhận diện và lưu hồ sơ thành công!', true);
    } catch (err) {
      setStatus({ state: 'error', message: '❌ Lỗi kết nối: ' + err.message });
      showToast('❌ Lỗi kết nối: ' + err.message, false);
    }
  };

  const handleApplyOracleData = (oracleData) => {
    if (!oracleData) return;
    setFormData((prev) => ({
      ...prev,
      so_cccd: oracleData.so_cccd || prev.so_cccd,
      ho_ten: oracleData.ho_ten || prev.ho_ten,
      ngay_sinh: oracleData.ngay_sinh || prev.ngay_sinh,
      gioi_tinh: oracleData.gioi_tinh || prev.gioi_tinh,
      quoc_tich: oracleData.quoc_tich || prev.quoc_tich,
      que_quan: oracleData.que_quan || prev.que_quan,
      noi_ctru: oracleData.noi_ctru || prev.noi_ctru,
      ngay_het_han: oracleData.ngay_het_han || prev.ngay_het_han,
    }));
    setShowEvalModal(false);
    showToast('✅ Đã áp dụng dữ liệu AI chuẩn vào form!', true);
  };

  const resetFieldsOnly = () => {
    setFormData({
      so_cccd: '',
      ho_ten: '',
      ngay_sinh: '',
      gioi_tinh: '',
      quoc_tich: 'Việt Nam',
      que_quan: '',
      noi_ctru: '',
      ngay_het_han: '',
    });
    setCurrentScanId(null);
    setCurrentResultId(null);
    setEvaluationResult(null);
  };

  // NÚT LÀM MỚI / RESET FORM SAU KHI LƯU
  const resetScanState = (showFeedback = false) => {
    resetFieldsOnly();
    setPreviewSrc('');
    setFile(null);

    setStatus({ state: 'ready', message: '' });
    setSourceBadge('Sẵn sàng');
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (nativeCameraInputRef.current) nativeCameraInputRef.current.value = '';

    if (showFeedback) {
      showToast('Đã làm mới form, sẵn sàng nhận diện ảnh tiếp theo!');
    }
    if (dropzoneRef.current) {
      dropzoneRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  const handleSaveEdited = async (e) => {
    e.preventDefault();
    if (!currentResultId) {
      showToast('Chưa có hồ sơ nào được quét!', false);
      return;
    }

    setSaving(true);
    const payload = {
      id_number: formData.so_cccd.trim(),
      full_name: formData.ho_ten.trim(),
      dob: formatDateForApi(formData.ngay_sinh.trim()),
      gender: formData.gioi_tinh.trim(),
      nationality: formData.quoc_tich.trim(),
      origin_location: formData.que_quan.trim(),
      residence: formData.noi_ctru.trim(),
      expiry_date: formatDateForApi(formData.ngay_het_han.trim()),
    };

    try {
      const res = await apiUpdateResult(currentResultId, payload);
      const data = await res.json();
      if (res.ok) {
        showToast('✅ Đã lưu kết quả vào CSDL và ghi nhận độ đúng của AI!', true);
        if (onSaveSuccess) onSaveSuccess(data);
        // Tự động làm mới form để sẵn sàng quét ảnh khác theo yêu cầu người dùng
        resetScanState(false);
        setStatus({
          state: 'success',
          message: '✅ Hồ sơ vừa quét đã được lưu thành công vào CSDL. Sẵn sàng quét ảnh tiếp theo!',
        });
      } else {
        showToast('❌ Lỗi cập nhật: ' + (data.detail || 'Thất bại'), false);
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối server: ' + err.message, false);
    } finally {
      setSaving(false);
    }
  };

  const formatDateForApi = (dStr) => {
    if (!dStr) return null;
    const clean = dStr.trim();
    if (!clean || clean.toLowerCase().includes('không') || clean.toLowerCase().includes('vô')) return null;
    const parts = clean.split(/[\/\-.]/);
    if (parts.length === 3) {
      let day = parts[0].padStart(2, '0');
      let month = parts[1].padStart(2, '0');
      let year = parts[2];
      if (parts[0].length === 4) {
        year = parts[0];
        month = parts[1].padStart(2, '0');
        day = parts[2].padStart(2, '0');
      }
      return `${year}-${month}-${day}`;
    }
    return clean;
  };

  // Expose processFile for external camera capture
  ScanTab.processCameraCapture = (blob) => {
    processFile(blob, true, 'WEBCAM');
  };

  return (
    <div className="grid-scan">
      {/* KHUNG BÊN TRÁI: TẢI ẢNH / XEM ẢNH KHUNG MÀU */}
      <div className="card">
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#eff6ff', color: 'var(--primary)' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <rect x="3" y="3" width="18" height="18" rx="3" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </span>
            <span>Ảnh Phát Hiện Khung Màu (YOLOv8)</span>
          </span>
          <span className={`badge ${sourceBadge === 'Sẵn sàng' ? 'badge-success' : 'badge-primary'}`}>
            {sourceBadge}
          </span>
        </h2>

        <div
          className="dropzone"
          id="dropzone"
          ref={dropzoneRef}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              const dropped = e.dataTransfer.files[0];
              const isVideo = (dropped.type && dropped.type.startsWith('video/')) || /\.(mp4|avi|mov|mkv|webm)$/i.test(dropped.name || '');
              processFile(dropped, false, isVideo ? 'VIDEO' : 'IMAGE');
            }
          }}
        >
          <div className="dropzone-icon">
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ width: '48px', height: '48px', color: 'var(--primary)' }}>
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)', display: 'block' }}>
            Kéo thả ảnh hoặc video CCCD vào đây hoặc bấm để chọn
          </strong>
          <p style={{ color: 'var(--text-muted)', marginTop: '6px', fontSize: '0.85rem', fontWeight: 500 }}>
            Hỗ trợ ảnh (JPG, PNG, WEBP) hoặc video (MP4, MOV, WEBM) từ máy tính
          </p>
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*,video/*"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <input
            type="file"
            ref={nativeCameraInputRef}
            accept="image/*"
            capture="environment"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>

        {/* NÚT THAO TÁC */}
        <div className="scan-btn-group">
          <button
            type="button"
            className="btn btn-outline"
            style={{ flex: 1 }}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <svg className="svg-icon" viewBox="0 0 24 24" style={{ color: '#64748b' }}>
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            </svg>
            Chọn File Từ Máy
          </button>
          <button
            type="button"
            className="btn btn-primary"
            style={{ flex: 1.25 }}
            onClick={onOpenCamModal}
          >
            <svg className="svg-icon" viewBox="0 0 24 24">
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="3" />
            </svg>
            Bật Camera Quét Thẻ
          </button>
        </div>

        {/* CÔNG TẮC THẨM ĐỊNH AI & CẤU HÌNH KEY NHANH */}
        <div
          style={{
            marginTop: '12px',
            padding: '12px 14px',
            background: '#f8fafc',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
            <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
              <input
                type="checkbox"
                checked={evaluateWithAi}
                onChange={(e) => setEvaluateWithAi(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--primary)', cursor: 'pointer' }}
              />
              <span>⚡ Tự động thẩm định & tính % độ chính xác AI</span>
            </label>
            <button
              type="button"
              onClick={() => setShowKeyBox(!showKeyBox)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary)',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>⚙️ {showKeyBox ? 'Đóng cấu hình Key' : 'Cấu hình API Key'}</span>
            </button>
          </div>

          {showKeyBox && (
            <div style={{ paddingTop: '10px', borderTop: '1px dashed #cbd5e1', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Trạng thái: {getUserAIKey() ? (
                  <strong style={{ color: '#0284c7' }}>🔑 Đang dùng Key cá nhân</strong>
                ) : systemKeyConfigured ? (
                  <strong style={{ color: '#16a34a' }}>🟢 Đang dùng Key hệ thống (.env)</strong>
                ) : (
                  <strong style={{ color: '#d97706' }}>⚪ Chưa cấu hình Key</strong>
                )}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="password"
                  placeholder="Dán Google Gemini API Key (AQ... hoặc AIzaSy...)"
                  value={quickKey}
                  onChange={(e) => setQuickKey(e.target.value)}
                  style={{ flex: 1, padding: '7px 10px', fontSize: '0.85rem', fontFamily: 'monospace' }}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSaveQuickKey}
                  style={{ padding: '7px 12px', fontSize: '0.8rem' }}
                >
                  Lưu
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleTestQuickKey}
                  disabled={isTestingQuickKey}
                  style={{ padding: '7px 12px', fontSize: '0.8rem' }}
                >
                  {isTestingQuickKey ? '...' : 'Kiểm tra'}
                </button>
              </div>
              {quickKeyMsg && (
                <div style={{ fontSize: '0.8rem', color: quickKeyMsg.valid ? '#16a34a' : '#dc2626', fontWeight: 500 }}>
                  {quickKeyMsg.valid ? '✅ ' : '❌ '}{quickKeyMsg.message}
                </div>
              )}
            </div>
          )}
        </div>

        {previewSrc && (
          <img
            src={previewSrc}
            id="preview"
            className="preview-img"
            alt="Ảnh nhận diện CCCD"
            style={{ display: 'block' }}
          />
        )}

        {status.message && (
          <div className={`status ${status.state}`}>
            {status.message}
          </div>
        )}
      </div>

      {/* KHUNG BÊN PHẢI: ĐỦ 8 TRƯỜNG DỮ LIỆU & NÚT LƯU KẾT QUẢ VÀO CSDL */}
      <div className="card">
        <h2>
          <span className="card-title-left">
            <span className="card-icon-badge" style={{ background: '#ecfdf5', color: '#059669' }}>
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                <rect x="8" y="2" width="8" height="4" rx="1" />
                <path d="m9 14 2 2 4-4" />
              </svg>
            </span>
            <span>Kết Quả Trích Xuất (Đủ 8 trường)</span>
          </span>
          <span className="badge badge-success">Chuẩn Căn Cước 2024</span>
        </h2>

        {/* BANNER ĐỘ CHÍNH XÁC AI */}
        {evaluationResult && evaluationResult.status === 'success' && (
          <div
            style={{
              background: '#f8fafc',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
              flexWrap: 'wrap',
              gap: '10px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.3rem' }}>🎯</span>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, color: '#0f172a' }}>Độ chính xác AI:</span>
                  <span
                    style={{
                      fontWeight: 800,
                      fontSize: '1.1rem',
                      color:
                        evaluationResult.overall_accuracy >= 95
                          ? '#16a34a'
                          : evaluationResult.overall_accuracy >= 85
                          ? '#0284c7'
                          : '#d97706'
                    }}
                  >
                    {evaluationResult.overall_accuracy}%
                  </span>
                  <span
                    className={`badge ${
                      evaluationResult.overall_accuracy >= 95
                        ? 'badge-success'
                        : evaluationResult.overall_accuracy >= 85
                        ? 'badge-info'
                        : 'badge-warning'
                    }`}
                    style={{ fontSize: '0.75rem', padding: '2px 6px' }}
                  >
                    {evaluationResult.overall_accuracy >= 95 ? 'Xuất Sắc' : evaluationResult.overall_accuracy >= 85 ? 'Tốt' : 'Khá'}
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '2px' }}>
                  Khớp {evaluationResult.matched_fields}/{evaluationResult.total_fields} trường • {evaluationResult.key_source === 'user' ? 'Key Cá Nhân' : 'Key Mặc Định .env'}
                </div>
              </div>
            </div>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleOpenEvalDetail}
              style={{ padding: '6px 12px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>🔍 Xem Chi Tiết Đối Soát</span>
            </button>
          </div>
        )}

        {evaluationResult && evaluationResult.status === 'error' && (
          <div
            style={{
              background: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '10px 14px',
              marginBottom: '16px',
              fontSize: '0.85rem',
              color: '#991b1b',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>⚠️</span>
            <span>{evaluationResult.message}</span>
          </div>
        )}

        <form onSubmit={handleSaveEdited}>

          <div className="field-group">
            <label>1. Số Căn cước công dân (12 số chuẩn)</label>
            <input
              type="text"
              value={formData.so_cccd}
              placeholder="Chờ quét..."
              onChange={(e) => handleFieldChange('so_cccd', e.target.value)}
            />
          </div>

          <div className="field-group">
            <label>2. Họ và tên</label>
            <input
              type="text"
              value={formData.ho_ten}
              placeholder="Chờ quét..."
              onChange={(e) => handleFieldChange('ho_ten', e.target.value)}
            />
          </div>

          <div className="field-row-grid">
            <div className="field-group">
              <label>3. Ngày sinh</label>
              <input
                type="text"
                value={formData.ngay_sinh}
                placeholder="DD/MM/YYYY"
                onChange={(e) => handleFieldChange('ngay_sinh', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>4. Giới tính</label>
              <input
                type="text"
                value={formData.gioi_tinh}
                placeholder="Nam / Nữ"
                onChange={(e) => handleFieldChange('gioi_tinh', e.target.value)}
              />
            </div>
          </div>

          <div className="field-row-grid">
            <div className="field-group">
              <label>5. Quốc tịch</label>
              <input
                type="text"
                value={formData.quoc_tich}
                placeholder="Việt Nam"
                onChange={(e) => handleFieldChange('quoc_tich', e.target.value)}
              />
            </div>
            <div className="field-group">
              <label>8. Có giá trị đến</label>
              <input
                type="text"
                value={formData.ngay_het_han}
                placeholder="DD/MM/YYYY"
                onChange={(e) => handleFieldChange('ngay_het_han', e.target.value)}
              />
            </div>
          </div>

          <div className="field-group">
            <label>6. Quê quán</label>
            <textarea
              rows={2}
              value={formData.que_quan}
              placeholder="Chờ quét..."
              onChange={(e) => handleFieldChange('que_quan', e.target.value)}
            />
          </div>

          <div className="field-group">
            <label>7. Nơi thường trú</label>
            <textarea
              rows={2}
              value={formData.noi_ctru}
              placeholder="Chờ quét..."
              onChange={(e) => handleFieldChange('noi_ctru', e.target.value)}
            />
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-success"
              style={{ flex: 2, padding: '13px' }}
              disabled={!currentResultId || saving}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                <polyline points="17 21 17 13 7 13 7 21" />
                <polyline points="7 3 7 8 15 8" />
              </svg>
              {saving ? 'Đang lưu vào CSDL...' : 'Xác Nhận & Lưu Kết Quả Vào CSDL'}
            </button>
            <button
              type="button"
              className="btn btn-outline"
              style={{ flex: 1, padding: '13px' }}
              onClick={() => resetScanState(true)}
            >
              <svg className="svg-icon" viewBox="0 0 24 24">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                <path d="M8 16H3v5" />
              </svg>
              Làm Mới
            </button>
          </div>
        </form>
      </div>

      {/* BẢNG ĐỐI SOÁT CHI TIẾT AI (DÀN HẾT RA TOÀN BỘ 2 CỘT & AUTO-SCROLL) */}
      {showEvalModal && evaluationResult && (
        <div
          ref={evalSectionRef}
          style={{
            gridColumn: '1 / -1',
            width: '100%',
            scrollMarginTop: '20px'
          }}
        >
          <AIComparisonModal
            evaluation={evaluationResult}
            onClose={() => setShowEvalModal(false)}
            onApplyOracle={handleApplyOracleData}
          />
        </div>
      )}
    </div>
  );
}

