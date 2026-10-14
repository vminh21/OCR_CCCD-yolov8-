// frontend/src/utils/exportPdf.js

export function exportCccdPdf(record) {
  if (!record) return;

  const printWindow = window.open('', '_blank', 'width=950,height=1000');
  if (!printWindow) {
    alert('Trình duyệt đã chặn cửa sổ Popup. Vui lòng cho phép Popups để xuất PDF!');
    return;
  }

  const savedDate = record.saved_at
    ? new Date(record.saved_at).toLocaleString('vi-VN')
    : new Date().toLocaleString('vi-VN');

  const cardImg = record.crop_image_path
    ? `${record.crop_image_path}?t=${record.id}`
    : '/media/cccd_fields_visualization.jpg';

  const avatarImg = record.avatar_path
    ? `${record.avatar_path}?t=${record.id}`
    : '';

  const htmlContent = `
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Ho_So_CCCD_${record.id_number || record.id}.pdf</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4 portrait;
      margin: 15mm 15mm 15mm 15mm;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #0f172a;
      background: #f8fafc;
      padding: 24px;
      line-height: 1.5;
    }
    .page-container {
      max-width: 800px;
      margin: 0 auto;
      background: #ffffff;
      padding: 36px 40px;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .no-print-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #1877f2;
      color: white;
      padding: 14px 20px;
      border-radius: 8px;
      max-width: 800px;
      margin: 0 auto 20px auto;
      box-shadow: 0 4px 12px rgba(24, 119, 242, 0.25);
    }
    .btn-action {
      padding: 8px 18px;
      border-radius: 6px;
      font-weight: 700;
      cursor: pointer;
      border: none;
      font-size: 0.9rem;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-print {
      background: #ffffff;
      color: #1877f2;
    }
    .btn-print:hover {
      background: #f1f5f9;
    }
    .btn-close {
      background: rgba(255,255,255,0.2);
      color: white;
      margin-left: 8px;
    }
    .btn-close:hover {
      background: rgba(255,255,255,0.3);
    }

    .national-header {
      text-align: center;
      margin-bottom: 22px;
    }
    .national-header .title-top {
      font-size: 13pt;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: #0f172a;
    }
    .national-header .title-sub {
      font-size: 11pt;
      font-weight: 700;
      margin-top: 2px;
      color: #334155;
    }
    .national-header .divider-line {
      width: 150px;
      height: 1.5px;
      background: #0f172a;
      margin: 6px auto 16px auto;
    }
    .doc-main-title {
      font-size: 16pt;
      font-weight: 800;
      color: #1877f2;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    .doc-meta {
      font-size: 9.5pt;
      color: #64748b;
      font-style: italic;
    }

    .photos-row {
      display: flex;
      gap: 16px;
      margin: 20px 0;
      align-items: stretch;
      justify-content: center;
    }
    .card-photo-panel {
      flex: 3;
      border: 1.5px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px;
      background: #f8fafc;
      text-align: center;
    }
    .card-photo-panel img {
      max-width: 100%;
      height: 195px;
      object-fit: contain;
      border-radius: 6px;
      background: #ffffff;
    }
    .avatar-photo-panel {
      flex: 1.1;
      border: 1.5px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px;
      background: #f8fafc;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .avatar-photo-panel img {
      width: 100%;
      max-width: 120px;
      height: 155px;
      object-fit: cover;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
    }
    .caption-tag {
      font-size: 8.5pt;
      font-weight: 600;
      color: #64748b;
      margin-top: 6px;
    }

    .table-data {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
      font-size: 10pt;
    }
    .table-data th, .table-data td {
      border: 1px solid #cbd5e1;
      padding: 9px 12px;
      text-align: left;
    }
    .table-data th {
      background: #f1f5f9;
      font-weight: 700;
      color: #334155;
      width: 32%;
    }
    .table-data td {
      color: #0f172a;
      background: #ffffff;
    }
    .highlight-id {
      font-weight: 800;
      color: #1877f2;
      font-size: 11.5pt;
      letter-spacing: 0.5px;
    }
    .highlight-name {
      font-weight: 800;
      color: #0f172a;
      font-size: 11pt;
      text-transform: uppercase;
    }
    .badge-status {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 8.5pt;
    }
    .badge-completed {
      background: #ecfdf5;
      color: #059669;
      border: 1px solid #a7f3d0;
    }
    .badge-edited {
      background: #fffbeb;
      color: #d97706;
      border: 1px solid #fde68a;
    }

    .signatures-row {
      display: flex;
      justify-content: space-between;
      margin-top: 36px;
      padding: 0 35px;
      text-align: center;
    }
    .sig-block .sig-role {
      font-size: 10pt;
      font-weight: 700;
      color: #0f172a;
      text-transform: uppercase;
    }
    .sig-block .sig-hint {
      font-size: 8.5pt;
      color: #64748b;
      font-style: italic;
      margin-top: 2px;
    }
    .sig-block .sig-placeholder {
      height: 65px;
    }
    .sig-block .sig-footer-title {
      font-size: 9.5pt;
      font-weight: 700;
      color: #1e293b;
    }

    @media print {
      body {
        padding: 0 !important;
        background: transparent !important;
      }
      .page-container {
        padding: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        max-width: 100% !important;
      }
      .no-print-toolbar {
        display: none !important;
      }
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
    }
  </style>
</head>
<body>
  <div class="no-print-toolbar">
    <div>
      <strong style="font-size: 1.05rem;">📄 Xuất Phiếu Hồ Sơ CCCD #${record.id}</strong>
      <p style="font-size: 0.82rem; opacity: 0.9; margin-top: 2px;">
        Nhấn nút <strong>Lưu / In PDF</strong> để mở hộp thoại in của trình duyệt và chọn "Lưu dưới dạng PDF" (Save as PDF).
      </p>
    </div>
    <div>
      <button class="btn-action btn-print" onclick="window.print()">
        🖨️ Lưu / In PDF
      </button>
      <button class="btn-action btn-close" onclick="window.close()">
        ✕ Đóng
      </button>
    </div>
  </div>

  <div class="page-container">
    <div class="national-header">
      <div class="title-top">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
      <div class="title-sub">Độc lập - Tự do - Hạnh phúc</div>
      <div class="divider-line"></div>
      <div class="doc-main-title">PHIẾU TRÍCH XUẤT THÔNG TIN CĂN CƯỚC CÔNG DÂN</div>
      <div class="doc-meta">
        Hệ thống AI nhận diện YOLOv8 + VietOCR • Hồ sơ #${record.id} • Thời gian lưu: ${savedDate}
      </div>
    </div>

    <div class="photos-row">
      <div class="card-photo-panel">
        <img src="${cardImg}" alt="Ảnh mặt trước thẻ CCCD" />
        <div class="caption-tag">Ảnh phát hiện & khoanh vùng thẻ CCCD (YOLOv8)</div>
      </div>
      ${avatarImg ? `
      <div class="avatar-photo-panel">
        <img src="${avatarImg}" alt="Ảnh chân dung" />
        <div class="caption-tag">Ảnh chân dung</div>
      </div>
      ` : ''}
    </div>

    <table class="table-data">
      <tbody>
        <tr>
          <th>1. Số Căn cước công dân:</th>
          <td class="highlight-id">${record.id_number || '---'}</td>
        </tr>
        <tr>
          <th>2. Họ và tên:</th>
          <td class="highlight-name">${record.full_name || '---'}</td>
        </tr>
        <tr>
          <th>3. Ngày sinh:</th>
          <td>${record.dob || '---'}</td>
        </tr>
        <tr>
          <th>4. Giới tính:</th>
          <td>${record.gender || '---'}</td>
        </tr>
        <tr>
          <th>5. Quốc tịch:</th>
          <td>${record.nationality || 'Việt Nam'}</td>
        </tr>
        <tr>
          <th>6. Quê quán:</th>
          <td>${record.origin_location || '---'}</td>
        </tr>
        <tr>
          <th>7. Nơi thường trú:</th>
          <td>${record.residence || '---'}</td>
        </tr>
        <tr>
          <th>8. Có giá trị đến:</th>
          <td>${record.expiry_date || '---'}</td>
        </tr>
        <tr>
          <th>Đánh giá kiểm định hệ thống:</th>
          <td>
            <span class="badge-status ${record.status === 'EDITED' ? 'badge-edited' : 'badge-completed'}">
              ${record.status === 'EDITED' ? '⚠️ Đã hiệu chỉnh bởi người dùng' : '✅ Đạt chuẩn tự động (AI Auto-Extracted)'}
            </span>
            ${record.confidence_score ? ` <span style="color: #64748b; font-size: 8.5pt;">(Độ tin cậy: ${(record.confidence_score * 100).toFixed(1)}%)</span>` : ''}
          </td>
        </tr>
      </tbody>
    </table>

    <div class="signatures-row">
      <div class="sig-block">
        <div class="sig-role">NGƯỜI XUẤT PHIẾU</div>
        <div class="sig-sub">(Ký và ghi rõ họ tên)</div>
        <div class="sig-placeholder"></div>
        <div class="sig-footer-title">Xác nhận sao y</div>
      </div>
      <div class="sig-block">
        <div class="sig-role">HỆ THỐNG OCR CCCD NHÓM 10</div>
        <div class="sig-sub">(Xác nhận số điện tử)</div>
        <div class="sig-placeholder"></div>
        <div class="sig-footer-title">74DCTT24 - AI Engine</div>
      </div>
    </div>
  </div>

  <script>
    window.addEventListener('load', () => {
      setTimeout(() => {
        window.print();
      }, 500);
    });
  </script>
</body>
</html>
`;

  printWindow.document.open();
  printWindow.document.write(htmlContent);
  printWindow.document.close();
}
