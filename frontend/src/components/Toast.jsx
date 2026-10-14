// frontend/src/components/Toast.jsx
import React from 'react';

export default function Toast({ toast }) {
  if (!toast || !toast.message) return null;

  return (
    <div
      id="toast"
      className="show"
      style={{
        borderLeft: toast.isSuccess ? '4px solid #42b72a' : '4px solid #fa383e',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>{toast.message}</span>
      </div>
    </div>
  );
}
