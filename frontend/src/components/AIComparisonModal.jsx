// frontend/src/components/AIComparisonModal.jsx
import React from 'react';

export default function AIComparisonModal({ evaluation, onClose, onApplyOracle }) {
  if (!evaluation) return null;

  const {
    overall_accuracy,
    matched_fields,
    total_fields,
    field_accuracies = [],
    provider = 'gemini',
    key_source = 'env',
    message
  } = evaluation;

  const getScoreColor = (score) => {
    if (score >= 95) return '#16a34a'; // Xanh lá đậm
    if (score >= 85) return '#0284c7'; // Xanh dương
    if (score >= 70) return '#d97706'; // Vàng cam
    return '#dc2626'; // Đỏ
  };

  const getScoreBadge = (score) => {
    if (score >= 95) return 'badge-success';
    if (score >= 85) return 'badge-info';
    if (score >= 70) return 'badge-warning';
    return 'badge-danger';
  };

  const overallColor = getScoreColor(overall_accuracy || 0);

  return (
    <div
      className="card"
      style={{
        width: '100%',
        marginTop: '16px',
        border: '1px solid #cbd5e1',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)',
        background: '#ffffff',
        animation: 'fadeIn 0.3s ease-in-out'
      }}
    >
      {/* HEADER CỦA BẢNG ĐỐI SOÁT */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #e2e8f0',
          paddingBottom: '16px',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '12px'
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: '#ecfdf5',
                color: '#059669',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.1rem'
              }}
            >
              ⚡
            </span>
            <span>Bảng Đối Soát Chi Tiết Độ Chính Xác OCR với AI Giám Khảo (Ground Truth)</span>
          </h2>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: '#64748b' }}>
              Mô hình Oracle: <strong style={{ color: '#0f172a', textTransform: 'capitalize' }}>{provider === 'gemini' ? 'Google Gemini Vision Flash' : 'OpenAI GPT-4o-mini'}</strong>
            </span>
            <span>•</span>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '0.75rem',
                fontWeight: 600,
                background: key_source === 'user' ? '#e0f2fe' : '#f1f5f9',
                color: key_source === 'user' ? '#0369a1' : '#475569'
              }}
            >
              {key_source === 'user' ? '🔑 Key Cá Nhân (User)' : '🌐 Key Mặc Định Server (.env)'}
            </span>
          </div>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onClose}
          style={{ padding: '8px 14px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <span>🔼 Thu Gọn Bảng Đối Soát</span>
        </button>
      </div>

      {/* TỔNG QUAN ĐIỂM SỐ & THỐNG KÊ */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          background: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '24px'
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Độ Chính Xác Tổng Thể
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '4px' }}>
            <span style={{ fontSize: '2.4rem', fontWeight: 800, color: overallColor, lineHeight: 1 }}>
              {overall_accuracy !== null && overall_accuracy !== undefined ? `${overall_accuracy}%` : '---'}
            </span>
            <span className={`badge ${getScoreBadge(overall_accuracy || 0)}`} style={{ fontSize: '0.85rem' }}>
              {overall_accuracy >= 95 ? '🌟 Xuất Sắc' : overall_accuracy >= 85 ? '✅ Tốt' : overall_accuracy >= 70 ? '⚠️ Khá' : '❌ Cần Cải Thiện'}
            </span>
          </div>
        </div>

        <div style={{ borderLeft: '2px solid #e2e8f0', paddingLeft: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#16a34a', lineHeight: 1 }}>
            {matched_fields}/{total_fields}
          </div>
          <div style={{ fontSize: '0.85rem', color: '#475569', marginTop: '4px' }}>Trường Khớp Hoàn Toàn 100%</div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>VietOCR đọc trùng khớp tuyệt đối</div>
        </div>

        <div style={{ borderLeft: '2px solid #e2e8f0', paddingLeft: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: total_fields - matched_fields > 0 ? '#d97706' : '#16a34a', lineHeight: 1 }}>
            {total_fields - matched_fields}
          </div>
          <div style={{ fontSize: '0.85rem', color: '#475569', marginTop: '4px' }}>Trường Có Chênh Lệch Ký Tự</div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Cần đối chiếu với ảnh gốc</div>
        </div>
      </div>

      {/* BẢNG ĐỐI CHIẾU CHI TIẾT DÀN HẾT TOÀN BỘ 100% CHIỀU RỘNG */}
      <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
        <table className="data-table" style={{ width: '100%', fontSize: '0.9rem', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ width: '18%', padding: '12px 14px' }}>Trường Thông Tin</th>
              <th style={{ width: '30%', padding: '12px 14px' }}>Kết Quả VietOCR (Trích Xuất)</th>
              <th style={{ width: '30%', padding: '12px 14px' }}>Chuẩn AI (Ground Truth)</th>
              <th style={{ width: '11%', textAlign: 'center', padding: '12px 10px' }}>Độ Khớp</th>
              <th style={{ width: '11%', textAlign: 'center', padding: '12px 10px' }}>Trạng Thái</th>
            </tr>
          </thead>
          <tbody>
            {field_accuracies.map((item, idx) => {
              const acc = item.accuracy_percent ?? 0;
              const isMatch = item.is_match;
              const accColor = getScoreColor(acc);

              return (
                <tr
                  key={idx}
                  style={{
                    background: isMatch ? '#ffffff' : '#fffbeb',
                    borderBottom: '1px solid #f1f5f9'
                  }}
                >
                  <td style={{ fontWeight: 600, color: '#1e293b', padding: '12px 14px' }}>
                    {item.field_label}
                    <div style={{ fontSize: '0.7rem', color: '#94a3b8', fontWeight: 400 }}>
                      Trọng số: {Math.round((item.weight || 0) * 100)}%
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', wordBreak: 'break-word', color: isMatch ? '#0f172a' : '#b45309', padding: '12px 14px', fontSize: '0.92rem' }}>
                    {item.local_value || <em style={{ color: '#94a3b8' }}>(Trống)</em>}
                  </td>
                  <td style={{ fontFamily: 'monospace', wordBreak: 'break-word', color: '#0f172a', padding: '12px 14px', fontSize: '0.92rem' }}>
                    {item.oracle_value || <em style={{ color: '#94a3b8' }}>(Trống)</em>}
                  </td>
                  <td style={{ textAlign: 'center', fontWeight: 700, color: accColor, padding: '12px 10px', fontSize: '0.95rem' }}>
                    {acc}%
                  </td>
                  <td style={{ textAlign: 'center', padding: '12px 10px' }}>
                    {isMatch ? (
                      <span className="badge badge-success" style={{ fontSize: '0.75rem', padding: '3px 8px' }}>
                        ✅ Khớp 100%
                      </span>
                    ) : (
                      <span className="badge badge-warning" style={{ fontSize: '0.75rem', padding: '3px 8px' }}>
                        ⚠️ Lệch ký tự
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* CHI TIẾT KÝ TỰ LỆCH (VISUAL DIFF CHO TRƯỜNG SAI NẾU CÓ) */}
      {field_accuracies.some((f) => !f.is_match && f.diffs && f.diffs.length > 0) && (
        <div style={{ marginBottom: '24px', background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
          <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: '#334155', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>🔍 Bản Đồ Phân Tích Sai Lệch Từng Ký Tự:</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 400, color: '#64748b' }}>
              (Ký tự <span style={{ background: '#fee2e2', color: '#dc2626', textDecoration: 'line-through', padding: '1px 4px', borderRadius: '3px' }}>gạch đỏ</span>: VietOCR đọc nhầm/thừa; <span style={{ background: '#dcfce7', color: '#16a34a', fontWeight: 600, padding: '1px 4px', borderRadius: '3px' }}>xanh lá</span>: Chuẩn AI)
            </span>
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {field_accuracies
              .filter((f) => !f.is_match && f.diffs && f.diffs.length > 0)
              .map((f, i) => (
                <div
                  key={i}
                  style={{
                    padding: '10px 14px',
                    background: '#ffffff',
                    border: '1px solid #cbd5e1',
                    borderRadius: '8px',
                    fontSize: '0.85rem'
                  }}
                >
                  <div style={{ fontWeight: 600, color: '#475569', marginBottom: '6px' }}>
                    {f.field_label}:
                  </div>
                  <div style={{ fontFamily: 'monospace', fontSize: '0.95rem', background: '#f8fafc', padding: '8px 12px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                    {f.diffs.map((d, di) => {
                      if (d.type === 'equal') {
                        return <span key={di} style={{ color: '#0f172a' }}>{d.text}</span>;
                      }
                      if (d.type === 'replace') {
                        return (
                          <span key={di}>
                            <span style={{ background: '#fee2e2', color: '#dc2626', textDecoration: 'line-through', padding: '1px 3px', borderRadius: '3px', marginRight: '2px' }}>
                              {d.local}
                            </span>
                            <span style={{ background: '#dcfce7', color: '#16a34a', fontWeight: 600, padding: '1px 3px', borderRadius: '3px' }}>
                              {d.oracle}
                            </span>
                          </span>
                        );
                      }
                      if (d.type === 'delete') {
                        return (
                          <span key={di} style={{ background: '#fee2e2', color: '#dc2626', textDecoration: 'line-through', padding: '1px 3px', borderRadius: '3px' }}>
                            {d.text}
                          </span>
                        );
                      }
                      if (d.type === 'insert') {
                        return (
                          <span key={di} style={{ background: '#dcfce7', color: '#16a34a', fontWeight: 600, padding: '1px 3px', borderRadius: '3px' }}>
                            {d.text}
                          </span>
                        );
                      }
                      return null;
                    })}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* FOOTER NÚT BẤM */}
      <div
        style={{
          borderTop: '1px solid #e2e8f0',
          paddingTop: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}
      >
        {onApplyOracle && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => onApplyOracle(evaluation.oracle_raw)}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 18px' }}
          >
            <span>📋 Áp Dụng Dữ Liệu AI Chuẩn Vào Form</span>
          </button>
        )}
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onClose}
          style={{ marginLeft: 'auto', padding: '10px 18px' }}
        >
          🔼 Thu Gọn Bảng Đối Soát
        </button>
      </div>
    </div>
  );
}
