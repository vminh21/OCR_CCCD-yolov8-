# main.py - FastAPI Web Service for OCR_CCCD (Nhóm 10 - 74DCTT24)
import os
import base64
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import sys
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Thêm đường dẫn root vào sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from src.core.pipeline import process_cccd
from src.api.routes import router as api_router

app = FastAPI(
    title="CCCD OCR API Service",
    description="Hệ thống AI nhận diện và trích xuất dữ liệu CCCD (YOLOv8 + VietOCR + PostgreSQL)",
    version="2.0.0"
)

# Đăng ký REST API Router
app.include_router(api_router)

# Mount thư mục tĩnh lưu trữ media
Path("data/output").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="data/output"), name="media")

HTML_UI = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CCCD AI • Hệ Thống Nhận Diện CCCD Việt Nam (Nhóm 10 - 74DCTT24)</title>
    <!-- MODERN TYPOGRAPHY: PLUS JAKARTA SANS & INTER -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        .svg-icon {
            display: inline-block;
            width: 1.15em;
            height: 1.15em;
            stroke-width: 2;
            stroke: currentColor;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
            vertical-align: -0.2em;
            flex-shrink: 0;
        }
        :root {
            /* FACEBOOK DESIGN SYSTEM TOKENS */
            --bg-canvas: #f0f2f5;           /* Facebook Canvas Gray */
            --bg-card: #ffffff;             /* Facebook Card White */
            --bg-card-subtle: #f0f2f5;
            --border-color: #ced0d4;        /* Facebook Border */
            --border-color-hover: #bec3c9;
            --divider: #e4e6eb;
            
            --primary: #1877f2;             /* Facebook Classic Blue */
            --primary-hover: #166fe5;
            --primary-active: #0e5a9e;
            --primary-subtle: #e7f3ff;      /* Facebook Highlight Light Blue */
            --primary-border: #adc8e6;
            
            --secondary: #4b4f56;
            --success: #42b72a;             /* Facebook Green Confirm */
            --success-hover: #36a420;
            --success-subtle: #e7f8ea;
            --success-border: #a3e9ab;
            
            --warning: #f59e0b;
            --warning-subtle: #fffbeb;
            --warning-border: #fde68a;
            
            --danger: #fa383e;              /* Facebook Red Alert */
            --danger-hover: #e41e3f;
            --danger-subtle: #fde8e8;
            --danger-border: #fca5a5;
            
            --text-main: #050505;           /* Facebook Title Black */
            --text-body: #1c1e21;           /* Facebook Body Dark */
            --text-muted: #65676b;          /* Facebook Secondary Gray */
            --text-disabled: #8a8d91;
            
            --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-card: 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 1px rgba(0, 0, 0, 0.08);
            --shadow-card-hover: 0 2px 8px rgba(0, 0, 0, 0.12);
            --shadow-modal: 0 12px 28px 0 rgba(0, 0, 0, 0.2), 0 2px 4px 0 rgba(0, 0, 0, 0.1);
            --shadow-primary: 0 2px 8px rgba(24, 119, 242, 0.3);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background: var(--bg-canvas);
            color: var(--text-body);
            min-height: 100vh;
            padding: 16px 20px 40px;
        }

        .container {
            max-width: 1320px;
            margin: 0 auto;
        }

        /* ============================================================== */
        /* NAVBAR / HEADER (FACEBOOK STYLE) */
        /* ============================================================== */
        header {
            position: sticky;
            top: 10px;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding: 10px 20px;
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            flex-wrap: wrap;
            gap: 12px;
            transition: all 0.2s ease;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }

        .logo-icon-box {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.35rem;
            box-shadow: 0 2px 6px rgba(24, 119, 242, 0.25);
        }

        .logo-title-group h1 {
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.3px;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo-title-group p {
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 500;
        }

        .user-nav {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .user-badge {
            background: #e4e6eb;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .user-avatar-circle {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #d8dadf;
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 800;
        }

        /* ============================================================== */
        /* BUTTON SYSTEM (FACEBOOK CLEAN STYLE - BORDER RADIUS 6PX) */
        /* ============================================================== */
        .btn {
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            border: none;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            outline: none;
        }

        .btn:disabled {
            opacity: 0.55;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }

        .btn-primary {
            background: var(--primary);
            color: #ffffff;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .btn-primary:hover:not(:disabled) {
            background: var(--primary-hover);
        }

        .btn-success {
            background: var(--success);
            color: #ffffff;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .btn-success:hover:not(:disabled) {
            background: var(--success-hover);
        }

        .btn-outline {
            background: #e4e6eb;
            color: var(--text-main);
            border: 1px solid transparent;
        }

        .btn-outline:hover:not(:disabled) {
            background: #d8dadf;
            color: var(--text-main);
        }

        .btn-danger {
            background: var(--danger);
            color: #ffffff;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .btn-danger:hover:not(:disabled) {
            background: var(--danger-hover);
            color: #ffffff;
        }

        /* ============================================================== */
        /* NAVIGATION TABS (FACEBOOK CLEAN STYLE - 8PX RADIUS) */
        /* ============================================================== */
        .tabs {
            display: flex;
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 4px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-card);
            gap: 4px;
            overflow-x: auto;
        }

        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 9px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            font-size: 0.88rem;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
            outline: none;
        }

        .tab-btn:hover {
            color: var(--text-main);
            background: #f0f2f5;
        }

        .tab-btn.active {
            color: var(--primary);
            background: var(--primary-subtle);
            border: 1px solid var(--primary-border);
        }

        /* TAB PANELS */
        .tab-panel { display: none; }
        .tab-panel.active { display: block; animation: tabFadeIn 0.2s ease; }
        @keyframes tabFadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ============================================================== */
        /* CARDS & SCAN GRID (FACEBOOK FEED STYLE - 8PX RADIUS) */
        /* ============================================================== */
        .grid-scan {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        @media (max-width: 980px) {
            .grid-scan { grid-template-columns: 1fr; }
            header { border-radius: 8px; }
            .tabs { border-radius: 8px; }
        }

        .card {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 20px 22px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-card);
            transition: box-shadow 0.2s ease;
        }

        .card:hover {
            box-shadow: var(--shadow-card-hover);
        }

        .card h2 {
            font-size: 1.08rem;
            font-weight: 700;
            margin-bottom: 18px;
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: space-between;
            letter-spacing: -0.2px;
        }

        .card-title-left {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-icon-badge {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        /* ============================================================== */
        /* DROPZONE (FACEBOOK STYLE - 8PX RADIUS) */
        /* ============================================================== */
        .dropzone {
            border: 2px dashed #1877f2;
            border-radius: 8px;
            padding: 30px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            background: #f0f2f5;
        }

        .dropzone:hover {
            border-color: #166fe5;
            background: #e7f3ff;
        }

        .dropzone-icon {
            width: 52px;
            height: 52px;
            margin: 0 auto 10px auto;
            border-radius: 8px;
            background: #e7f3ff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            color: #1877f2;
            transition: transform 0.2s;
        }

        .dropzone:hover .dropzone-icon {
            transform: scale(1.05);
        }

        .preview-img {
            width: 100%;
            max-height: 420px;
            object-fit: contain;
            border-radius: 8px;
            margin-top: 18px;
            display: none;
            border: 1px solid var(--border-color);
            background: #000;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        }

        /* ============================================================== */
        /* INPUT FIELDS & FORM (FACEBOOK STYLE - 6PX RADIUS) */
        /* ============================================================== */
        .field-group { margin-bottom: 14px; }
        .field-group label {
            display: block;
            font-size: 0.78rem;
            font-weight: 700;
            color: #65676b;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .field-group input, .field-group textarea {
            width: 100%;
            padding: 10px 14px;
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 600;
            outline: none;
            transition: all 0.15s ease;
        }

        .field-group input:focus, .field-group textarea:focus {
            background: #ffffff;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(24, 119, 242, 0.2);
        }

        .field-row-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        /* ============================================================== */
        /* STATUS ALERTS */
        /* ============================================================== */
        .status {
            margin-top: 14px;
            padding: 12px 16px;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
            display: none;
            animation: tabFadeIn 0.2s ease;
        }
        .status.loading {
            display: block;
            background: var(--primary-subtle);
            color: var(--primary);
            border: 1px solid var(--primary-border);
        }
        .status.success {
            display: block;
            background: var(--success-subtle);
            color: var(--success-hover);
            border: 1px solid var(--success-border);
        }
        .status.error {
            display: block;
            background: var(--danger-subtle);
            color: var(--danger);
            border: 1px solid var(--danger-border);
        }

        /* ============================================================== */
        /* TABLES & BADGES (FACEBOOK CLEAN - 8PX RADIUS) */
        /* ============================================================== */
        .data-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 14px;
            font-size: 0.88rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }

        .data-table th, .data-table td {
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid #f0f2f5;
        }

        .data-table th {
            background: #f0f2f5;
            color: #65676b;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .data-table tr:last-child td { border-bottom: none; }
        .data-table tbody tr {
            background: #ffffff;
            transition: background 0.15s ease;
        }
        .data-table tbody tr:hover {
            background: #f8fafc;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.2px;
        }
        .badge-success { background: var(--success-subtle); color: var(--success-hover); border: 1px solid var(--success-border); }
        .badge-warning { background: var(--warning-subtle); color: #d97706; border: 1px solid var(--warning-border); }
        .badge-primary { background: var(--primary-subtle); color: var(--primary); border: 1px solid var(--primary-border); }

        /* ============================================================== */
        /* STATS CARDS (FACEBOOK STYLE - 8PX RADIUS) */
        /* ============================================================== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: #ffffff;
            padding: 20px 22px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
            transition: all 0.2s ease;
        }

        .stat-card:hover {
            box-shadow: var(--shadow-card-hover);
        }

        .stat-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }

        .stat-val {
            font-size: 2.1rem;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: -0.5px;
            margin-top: 4px;
        }

        .stat-label {
            font-size: 0.78rem;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        /* ============================================================== */
        /* MODALS (FACEBOOK POPUP STYLE - 8PX RADIUS) */
        /* ============================================================== */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.45);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }

        .modal.active { display: flex; animation: modalPop 0.18s ease; }
        @keyframes modalPop {
            from { opacity: 0; transform: scale(0.97); }
            to { opacity: 1; transform: scale(1); }
        }

        .modal-content {
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 24px;
            width: 100%;
            max-width: 480px;
            box-shadow: var(--shadow-modal);
        }

        .field-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 9px 0;
            border-bottom: 1px solid #f0f2f5;
        }
        .field-row:last-child { border-bottom: none; }
        .field-title { font-size: 0.8rem; font-weight: 700; color: #65676b; text-transform: uppercase; }
        .field-val { font-size: 0.92rem; font-weight: 700; color: var(--text-main); text-align: right; }

        /* TOAST (FACEBOOK TOAST - 6PX RADIUS) */
        #toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            display: none;
            z-index: 2000;
            background: #242526;
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: toastPop 0.2s ease;
        }
        @keyframes toastPop {
            from { transform: translateY(10px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <!-- ============================================================== -->
    <!-- ============================================================== -->
    <!-- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ (FACEBOOK CARD STYLE) -->
    <!-- ============================================================== -->
    <div id="auth-screen" style="display: flex; min-height: 88vh; align-items: center; justify-content: center; padding: 20px; position: relative;">
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 8px; padding: 36px 32px; width: 100%; max-width: 440px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 8px 16px rgba(0, 0, 0, 0.1); position: relative; z-index: 1;">
            
            <div style="text-align: center; margin-bottom: 22px;">
                <div style="width: 52px; height: 52px; margin: 0 auto 12px auto; border-radius: 8px; background: var(--primary); display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 2px 8px rgba(24, 119, 242, 0.3);">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="width: 28px; height: 28px; color: white;"><rect x="2" y="4" width="20" height="16" rx="2"/><circle cx="8" cy="10" r="2.5"/><line x1="13" y1="9" x2="19" y2="9"/><line x1="13" y1="13" x2="19" y2="13"/><line x1="5" y1="16" x2="11" y2="16"/><line x1="14" y1="16" x2="19" y2="16"/></svg>
                </div>
                <h2 style="font-size: 1.6rem; font-weight: 800; color: #050505; letter-spacing: -0.4px;">CCCD <span style="color: var(--primary);">OCR</span></h2>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; font-weight: 500;">Hệ Thống AI Định Danh • Nhóm 10 - 74DCTT24</p>
            </div>

            <!-- TAB SWITCHER ĐĂNG NHẬP / ĐĂNG KÝ (FACEBOOK 6PX SWITCHER) -->
            <div style="display: flex; background: #e4e6eb; border-radius: 6px; padding: 4px; margin-bottom: 20px;">
                <button type="button" id="tab-btn-login" class="btn" style="flex: 1; justify-content: center; background: #ffffff; color: var(--primary); box-shadow: 0 1px 2px rgba(0,0,0,0.1);" onclick="switchAuthTab('login')">Đăng Nhập</button>
                <button type="button" id="tab-btn-register" class="btn" style="flex: 1; justify-content: center; background: transparent; color: var(--text-muted);" onclick="switchAuthTab('register')">Đăng Ký</button>
            </div>

            <div id="auth-alert" style="display: none; padding: 10px 14px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 16px; font-weight: 600;"></div>

            <!-- FORM ĐĂNG NHẬP -->
            <form id="form-login" onsubmit="event.preventDefault(); submitLogin();">
                <div class="field-group">
                    <label>Tên đăng nhập (Username)</label>
                    <input type="text" id="login-username" placeholder="Nhập username (VD: minh_final)..." required autocomplete="username">
                </div>
                <div class="field-group" style="margin-top: 12px;">
                    <label>Mật khẩu</label>
                    <input type="password" id="login-password" placeholder="Nhập mật khẩu..." required autocomplete="current-password">
                </div>
                <button type="submit" class="btn btn-primary" id="btn-login-submit" style="width: 100%; margin-top: 18px; padding: 11px; font-size: 0.95rem;">
                    <svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
                    Đăng Nhập Hệ Thống
                </button>

                <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--divider); text-align: center;">
                    <button type="button" class="btn btn-outline" style="width: 100%; font-size: 0.85rem;" onclick="quickLoginDemo()">
                        <svg class="svg-icon" viewBox="0 0 24 24" style="color: #f59e0b;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                        Đăng nhập nhanh tài khoản mẫu (minh_final)
                    </button>
                </div>
            </form>

            <!-- FORM ĐĂNG KÝ -->
            <form id="form-register" style="display: none;" onsubmit="event.preventDefault(); submitRegister();">
                <div class="field-group">
                    <label>Họ và tên hiển thị</label>
                    <input type="text" id="reg-fullname" placeholder="VD: Nguyễn Văn Minh" required>
                </div>
                <div class="field-group" style="margin-top: 10px;">
                    <label>Tên đăng nhập (Username)</label>
                    <input type="text" id="reg-username" placeholder="VD: minh123" required autocomplete="username">
                </div>
                <div class="field-group" style="margin-top: 10px;">
                    <label>Địa chỉ Email</label>
                    <input type="email" id="reg-email" placeholder="VD: minh@example.com" required autocomplete="email">
                </div>
                <div class="field-group" style="margin-top: 10px;">
                    <label>Mật khẩu (Tối thiểu 6 ký tự)</label>
                    <input type="password" id="reg-password" placeholder="Nhập mật khẩu..." required minlength="6" autocomplete="new-password">
                </div>
                <button type="submit" class="btn btn-success" id="btn-reg-submit" style="width: 100%; margin-top: 18px; padding: 11px; font-size: 0.95rem;">
                    <svg class="svg-icon" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
                    Tạo Tài Khoản & Vào Hệ Thống
                </button>
            </form>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- MÀN HÌNH ỨNG DỤNG CHÍNH (CCCD MAIN APP - SAU KHI ĐĂNG NHẬP) -->
    <!-- ============================================================== -->
    <div id="main-app" class="container" style="display: none;">
        <!-- TOP STICKY NAVBAR -->
        <header>
            <div class="logo-area">
                <div class="logo-icon-box">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="width: 22px; height: 22px; color: white;"><rect x="2" y="4" width="20" height="16" rx="3"/><circle cx="8" cy="10" r="2.5"/><line x1="13" y1="9" x2="19" y2="9"/><line x1="13" y1="13" x2="19" y2="13"/><line x1="5" y1="16" x2="11" y2="16"/><line x1="14" y1="16" x2="19" y2="16"/></svg>
                </div>
                <div class="logo-title-group">
                    <h1>CCCD <span style="color: var(--primary);">OCR</span></h1>
                    <p>YOLOv8 + VietOCR Transformer • Nhóm 10 - 74DCTT24</p>
                </div>
            </div>
            <div class="user-nav">
                <div class="user-badge" id="user-display">
                    <div class="user-avatar-circle">
                        <svg class="svg-icon" viewBox="0 0 24 24" style="width: 14px; height: 14px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    </div>
                    <span id="username-text">Người dùng</span>
                    <span id="user-sub" style="color: var(--text-muted); font-size: 0.78rem; font-weight: normal; margin-left: 2px;"></span>
                </div>
                <button class="btn btn-outline" onclick="openModal('modal-password')">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="color: #6366f1;"><circle cx="7.5" cy="15.5" r="4.5"/><path d="m21 3-9.5 9.5"/><path d="m15.5 7.5 3 3"/><path d="m18.5 4.5 2 2"/></svg>
                    Đổi mật khẩu
                </button>
                <button class="btn btn-danger" onclick="logoutUser()">
                    <svg class="svg-icon" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                    Đăng xuất
                </button>
            </div>
        </header>

        <!-- NAVIGATION TABS -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('tab-scan')">
                <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="12" cy="12" r="3.5"/><path d="M3 9h3M3 15h3M18 9h3M18 15h3"/></svg>
                1. Nhận Diện & Hiệu Chỉnh CCCD
            </button>
            <button class="tab-btn" onclick="switchTab('tab-results')">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                2. Bảng Lưu Kết Quả (8 Trường)
            </button>
            <button class="tab-btn" onclick="switchTab('tab-stats')">
                <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                3. Thống Kê & Độ Đúng Của AI
            </button>
            <button class="tab-btn" onclick="switchTab('tab-profile')">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                4. Quản Lý Tài Khoản
            </button>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 1: NHẬN DIỆN & HIỆU CHỈNH KẾT QUẢ -->
        <!-- ============================================================== -->
        <div id="tab-scan" class="tab-panel active">
            <div class="grid-scan">
                <!-- KHUNG BÊN TRÁI: TẢI ẢNH / XEM ẢNH KHUNG MÀU -->
                <div class="card">
                    <h2>
                        <span class="card-title-left">
                            <span class="card-icon-badge" style="background: #eff6ff; color: var(--primary);">
                                <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                            </span>
                            <span>Ảnh Phát Hiện Khung Màu (YOLOv8)</span>
                        </span>
                        <span id="source-badge" class="badge badge-success">Sẵn sàng</span>
                    </h2>
                    
                    <div class="dropzone" id="dropzone" onclick="document.getElementById('file-input').click()">
                        <div class="dropzone-icon">
                            <svg class="svg-icon" viewBox="0 0 24 24" style="width: 48px; height: 48px; color: var(--primary);"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                        </div>
                        <strong style="font-size: 1.05rem; color: var(--text-main); display: block;">Kéo thả ảnh CCCD vào đây hoặc bấm để chọn</strong>
                        <p style="color: var(--text-muted); margin-top: 6px; font-size: 0.85rem; font-weight: 500;">Hỗ trợ ảnh định dạng JPG, PNG, WEBP từ máy tính</p>
                        <input type="file" id="file-input" accept="image/*" style="display:none" onchange="uploadImage(event)">
                    </div>

                    <!-- NÚT THAO TÁC: CHỌN FILE HOẶC BẬT CAMERA QUÉT TRỰC TIẾP -->
                    <div style="display: flex; gap: 12px; margin-top: 14px; margin-bottom: 12px;">
                        <button type="button" class="btn btn-outline" style="flex: 1;" onclick="document.getElementById('file-input').click()">
                            <svg class="svg-icon" viewBox="0 0 24 24" style="color: #64748b;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                            Chọn File Từ Máy
                        </button>
                        <button type="button" class="btn btn-primary" style="flex: 1.25;" onclick="openCameraModal()">
                            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="3"/></svg>
                            Bật Camera Quét Thẻ
                        </button>
                    </div>

                    <!-- Ảnh hiển thị: Ảnh gốc lúc chọn -> Ảnh nắn phẳng vẽ 8 bounding box sau khi AI quét -->
                    <img id="preview" class="preview-img" alt="Ảnh nhận diện CCCD">
                    <div id="status" class="status"></div>
                </div>

                <!-- KHUNG BÊN PHẢI: ĐỦ 8 TRƯỜNG DỮ LIỆU & NÚT LƯU KẾT QUẢ VÀO CSDL -->
                <div class="card">
                    <h2>
                        <span class="card-title-left">
                            <span class="card-icon-badge" style="background: #ecfdf5; color: #059669;">
                                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="m9 14 2 2 4-4"/></svg>
                            </span>
                            <span>Kết Quả Trích Xuất (Đủ 8 trường)</span>
                        </span>
                        <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 500;">Chỉnh sửa trực tiếp ô chữ</span>
                    </h2>

                    <form id="edit-form" onsubmit="event.preventDefault(); saveEditedResult();">
                        <div class="field-row-grid">
                            <div class="field-group">
                                <label>1. Số CCCD (12 chữ số)</label>
                                <input type="text" id="val-so_cccd" placeholder="Chờ quét...">
                            </div>
                            <div class="field-group">
                                <label>2. Họ và tên</label>
                                <input type="text" id="val-ho_ten" placeholder="Chờ quét...">
                            </div>
                        </div>

                        <div class="field-row-grid">
                            <div class="field-group">
                                <label>3. Ngày sinh</label>
                                <input type="text" id="val-ngay_sinh" placeholder="DD/MM/YYYY">
                            </div>
                            <div class="field-group">
                                <label>4. Giới tính</label>
                                <input type="text" id="val-gioi_tinh" placeholder="Nam / Nữ">
                            </div>
                        </div>

                        <div class="field-row-grid">
                            <div class="field-group">
                                <label>5. Quốc tịch (Bổ sung đầy đủ)</label>
                                <input type="text" id="val-quoc_tich" value="Việt Nam">
                            </div>
                            <div class="field-group">
                                <label>8. Có giá trị đến</label>
                                <input type="text" id="val-ngay_het_han" placeholder="DD/MM/YYYY">
                            </div>
                        </div>

                        <div class="field-group">
                            <label>6. Quê quán</label>
                            <textarea id="val-que_quan" rows="2" placeholder="Chờ quét..."></textarea>
                        </div>

                        <div class="field-group">
                            <label>7. Nơi thường trú</label>
                            <textarea id="val-noi_ctru" rows="2" placeholder="Chờ quét..."></textarea>
                        </div>

                        <div style="margin-top: 20px; display: flex; gap: 12px;">
                            <button type="submit" id="btn-save" class="btn btn-success" style="flex: 1; padding: 13px;" disabled>
                                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                                Xác Nhận & Lưu Kết Quả Vào CSDL
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 2: BẢNG LƯU KẾT QUẢ (CCCD_RESULTS) -->
        <!-- ============================================================== -->
        <div id="tab-results" class="tab-panel">
            <div class="card">
                <h2>
                    <span class="card-title-left">
                        <span class="card-icon-badge" style="background: #eff6ff; color: var(--primary);">
                            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                        </span>
                        <span>Bảng Lưu Kết QuẢ Thẻ CCCD (cccd_results)</span>
                    </span>
                    <input type="text" id="search-input" placeholder="Tìm theo Số CCCD hoặc Họ tên..." oninput="loadResultsList()" 
                           style="padding: 8px 14px; background: #ffffff; border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-main); width: 280px; font-size: 0.88rem; font-weight: 500; outline: none;">
                </h2>

                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>#ID</th>
                                <th style="text-align:center;">Xem Thẻ</th>
                                <th>Số CCCD</th>
                                <th>Họ Và Tên</th>
                                <th>Ngày Sinh</th>
                                <th>Giới Tính</th>
                                <th>Quốc Tịch</th>
                                <th>Quê Quán</th>
                                <th>Nơi Thường Trú</th>
                                <th>Hạn Dùng</th>
                                <th>Thời Gian Lưu</th>
                                <th style="text-align:center;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody id="results-tbody">
                            <tr><td colspan="12" style="text-align:center; color:var(--text-muted); padding: 30px;">Đang tải dữ liệu...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 3: THỐNG KÊ & ĐÁNH GIÁ ĐỘ ĐÚNG AI (SCAN_STATISTICS & AI_CORRECTIONS) -->
        <!-- ============================================================== -->
        <div id="tab-stats" class="tab-panel">
            <!-- CARDS THỐNG KÊ (METRIC CARDS) -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card-header">
                        <div class="stat-label">Tổng Số Lượt Quét</div>
                        <span class="card-icon-badge" style="background: #eff6ff; color: var(--primary);">
                            <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                        </span>
                    </div>
                    <div class="stat-val" id="stat-total">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-header">
                        <div class="stat-label">Ảnh / Webcam / Video</div>
                        <span class="card-icon-badge" style="background: #f5f3ff; color: #7c3aed;">
                            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="3"/></svg>
                        </span>
                    </div>
                    <div class="stat-val" style="font-size: 1.6rem; color: #6366f1;" id="stat-sources">0 / 0 / 0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-header">
                        <div class="stat-label">Số Ca Phải Hiệu Chỉnh</div>
                        <span class="card-icon-badge" style="background: #fffbeb; color: #d97706;">
                            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                        </span>
                    </div>
                    <div class="stat-val" style="color: var(--warning);" id="stat-edited">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-header">
                        <div class="stat-label">Độ Tin Cậy AI Trung Bình</div>
                        <span class="card-icon-badge" style="background: #ecfdf5; color: #059669;">
                            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 14"/></svg>
                        </span>
                    </div>
                    <div class="stat-val" style="color: var(--success);" id="stat-confidence">0%</div>
                </div>
            </div>

            <!-- BẢNG ĐỐI SOÁT ĐỘ ĐÚNG CỦA AI VÀ LỊCH SỬ CHỈNH SỬA (ai_corrections) -->
            <div class="card">
                <h2>
                    <span class="card-title-left">
                        <span class="card-icon-badge" style="background: #eff6ff; color: var(--primary);">
                            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                        </span>
                        <span>Bảng Phân Chia Độ Đúng Của AI & Người Dùng Sửa Gì (ai_corrections)</span>
                    </span>
                    <button class="btn btn-outline" onclick="loadStatsAndCorrections()">
                        <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                        Làm mới
                    </button>
                </h2>
                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Lượt quét #</th>
                                <th>Trường Bị Sửa</th>
                                <th>AI Nhận Diện Ban Đầu</th>
                                <th>Người Dùng Sửa Lại</th>
                                <th>Đánh Giá AI</th>
                                <th>Độ Tin Cậy AI</th>
                                <th>Thời Điểm Sửa</th>
                            </tr>
                        </thead>
                        <tbody id="corrections-tbody">
                            <tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding: 30px;">Chưa có dữ liệu sửa đổi.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 4: QUẢN LÝ TÀI KHOẢN -->
        <!-- ============================================================== -->
        <div id="tab-profile" class="tab-panel">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                <!-- KHUNG 1: THÔNG TIN TÀI KHOẢN -->
                <div class="card">
                    <h2>
                        <span class="card-title-left">
                            <span class="card-icon-badge" style="background: #eff6ff; color: var(--primary);">
                                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                            </span>
                            <span>Thông Tin Tài Khoản</span>
                        </span>
                    </h2>
                    <div style="display: flex; flex-direction: column; gap: 16px; margin-top: 15px;">
                        <div class="field-group">
                            <label>Tên đăng nhập (Username):</label>
                            <input type="text" id="prof-username" readonly style="background: #f8fafc; color: var(--text-muted);">
                        </div>
                        <div class="field-group">
                            <label>Họ và tên người dùng:</label>
                            <input type="text" id="prof-fullname" readonly style="background: #f8fafc; color: var(--text-main); font-weight: 700;">
                        </div>
                        <div class="field-group">
                            <label>Email liên hệ:</label>
                            <input type="text" id="prof-email" readonly style="background: #f8fafc; color: var(--text-main);">
                        </div>
                        <div class="field-group">
                            <label>Thời điểm tạo tài khoản:</label>
                            <input type="text" id="prof-created" readonly style="background: #f8fafc; color: var(--text-muted);">
                        </div>
                        <div style="margin-top: 10px; display: flex; gap: 10px;">
                            <button type="button" class="btn btn-danger" onclick="logoutUser()">
                                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                                Đăng Xuất Khỏi Hệ Thống
                            </button>
                        </div>
                    </div>
                </div>

                <!-- KHUNG 2: ĐỔI MẬT KHẨU -->
                <div class="card">
                    <h2>
                        <span class="card-title-left">
                            <span class="card-icon-badge" style="background: #fef2f2; color: #dc2626;">
                                <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                            </span>
                            <span>Đổi Mật Khẩu Đăng Nhập</span>
                        </span>
                    </h2>
                    <form onsubmit="event.preventDefault(); submitTabChangePassword();" style="display: flex; flex-direction: column; gap: 16px; margin-top: 15px;">
                        <div class="field-group">
                            <label>Mật khẩu hiện tại:</label>
                            <input type="password" id="tab-old-pass" required placeholder="Nhập mật khẩu hiện tại...">
                        </div>
                        <div class="field-group">
                            <label>Mật khẩu mới:</label>
                            <input type="password" id="tab-new-pass" required minlength="6" placeholder="Tối thiểu 6 ký tự...">
                        </div>
                        <div class="field-group">
                            <label>Xác nhận mật khẩu mới:</label>
                            <input type="password" id="tab-confirm-pass" required minlength="6" placeholder="Nhập lại mật khẩu mới...">
                        </div>
                        <div style="margin-top: 10px;">
                            <button type="submit" class="btn btn-primary" style="padding: 12px 26px;">
                                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                                Cập Nhật Mật Khẩu
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL ĐỔI MẬT KHẨU -->
    <div id="modal-password" class="modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 18px; font-size: 1.25rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 8px;">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color: #6366f1;"><circle cx="7.5" cy="15.5" r="4.5"/><path d="m21 3-9.5 9.5"/><path d="m15.5 7.5 3 3"/><path d="m18.5 4.5 2 2"/></svg>
                Đổi Mật Khẩu Tài Khoản
            </h3>
            <form onsubmit="event.preventDefault(); submitChangePassword();">
                <div class="field-group">
                    <label>Mật khẩu hiện tại</label>
                    <input type="password" id="old-pass" required>
                </div>
                <div class="field-group">
                    <label>Mật khẩu mới</label>
                    <input type="password" id="new-pass" required minlength="6">
                </div>
                <div style="display: flex; gap: 12px; margin-top: 22px;">
                    <button type="submit" class="btn btn-primary" style="flex:1;">Lưu mật khẩu</button>
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-password')">Đóng</button>
                </div>
            </form>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- MODAL QUÉT CCCD TRỰC TIẾP BẰNG CAMERA (FACEBOOK STYLE MODAL) -->
    <!-- ============================================================== -->
    <div id="modal-camera" class="modal">
        <div class="modal-content" style="max-width: 720px; width: 95%; padding: 20px; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 34px; height: 34px; border-radius: 6px; background: var(--primary-subtle); display: flex; align-items: center; justify-content: center; color: var(--primary);">
                        <svg class="svg-icon" viewBox="0 0 24 24" style="width: 18px; height: 18px;"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
                    </div>
                    <div>
                        <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin: 0;">Quét & Nhận Diện CCCD Bằng Camera</h3>
                        <p style="font-size: 0.8rem; color: var(--text-muted); margin: 2px 0 0 0; font-weight: 500;">Căn chỉnh thẻ vào khung • Tự động chụp hoặc nhấn phím <strong style="color:var(--primary);">Space</strong> / nút Chụp</p>
                    </div>
                </div>
                <button type="button" class="btn btn-outline" style="padding: 4px 10px; border-radius: 4px;" onclick="closeCameraModal()">✕</button>
            </div>

            <!-- KHUNG CAMERA VIEWPORT -->
            <div id="camera-viewport" style="position: relative; width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border-color); box-shadow: inset 0 0 24px rgba(0,0,0,0.85);">
                <!-- Luồng Video Stream -->
                <video id="camera-video" autoplay playsinline muted style="width: 100%; height: 100%; object-fit: cover;"></video>
                <canvas id="camera-canvas" style="display: none;"></canvas>
                <!-- Canvas vẽ khung phát hiện YOLO trực tiếp trên video -->
                <canvas id="camera-overlay-canvas" style="position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 8;"></canvas>

                <!-- LỚP PHỦ CĂN THẺ (CARD GUIDE OVERLAY TỶ LỆ CHUẨN 1.586) -->
                <div id="camera-guide-box" style="position: absolute; width: 75%; max-width: 480px; aspect-ratio: 1.586; border: 2px dashed rgba(255, 255, 255, 0.7); border-radius: 6px; box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.52); pointer-events: none; transition: all 0.25s ease;">
                    <!-- 4 góc định vị xanh cyan -->
                    <div id="corner-tl" style="position: absolute; top: -3px; left: -3px; width: 24px; height: 24px; border-top: 3px solid #38bdf8; border-left: 3px solid #38bdf8; border-top-left-radius: 6px; transition: border-color 0.2s;"></div>
                    <div id="corner-tr" style="position: absolute; top: -3px; right: -3px; width: 24px; height: 24px; border-top: 3px solid #38bdf8; border-right: 3px solid #38bdf8; border-top-right-radius: 6px; transition: border-color 0.2s;"></div>
                    <div id="corner-bl" style="position: absolute; bottom: -3px; left: -3px; width: 24px; height: 24px; border-bottom: 3px solid #38bdf8; border-left: 3px solid #38bdf8; border-bottom-left-radius: 6px; transition: border-color 0.2s;"></div>
                    <div id="corner-br" style="position: absolute; bottom: -3px; right: -3px; width: 24px; height: 24px; border-bottom: 3px solid #38bdf8; border-right: 3px solid #38bdf8; border-bottom-right-radius: 6px; transition: border-color 0.2s;"></div>
                    
                    <!-- Nhãn chữ giữa khung -->
                    <div id="guide-center-text" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.85); font-size: 0.85rem; font-weight: 600; text-shadow: 0 1px 4px rgba(0,0,0,0.9); pointer-events: none;">
                        Đặt mặt trước thẻ CCCD vào khung
                    </div>
                </div>

                <!-- BADGE TRẠNG THÁI THỜI GIAN THỰC -->
                <div id="camera-status-badge" style="position: absolute; top: 12px; left: 50%; transform: translateX(-50%); background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(8px); color: #38bdf8; padding: 6px 14px; border-radius: 4px; font-size: 0.82rem; font-weight: 700; border: 1px solid rgba(56, 189, 248, 0.4); display: flex; align-items: center; gap: 8px; z-index: 10; pointer-events: none;">
                    <span id="camera-status-dot" style="width: 8px; height: 8px; background: #38bdf8; border-radius: 50%; display: inline-block;"></span>
                    <span id="camera-status-text">Đang tìm kiếm thẻ CCCD...</span>
                </div>

                <!-- VÒNG ĐẾM NGƯỢC TỰ ĐỘNG CHỤP -->
                <div id="camera-countdown" style="display: none; position: absolute; inset: 0; background: rgba(0,0,0,0.6); z-index: 20; align-items: center; justify-content: center; flex-direction: column; backdrop-filter: blur(3px);">
                    <div id="countdown-number" style="font-size: 4.5rem; font-weight: 900; color: #10b981; text-shadow: 0 0 25px rgba(16, 185, 129, 0.9);">1</div>
                    <div style="font-size: 1rem; color: #fff; font-weight: 700; margin-top: 6px;">🟢 ĐÃ BẮT ĐƯỢC THẺ CHUẨN! GIỮ YÊN...</div>
                </div>

                <!-- HIỆU ỨNG FLASH TRẮNG KHI CHỤP -->
                <div id="camera-flash" style="display: none; position: absolute; inset: 0; background: #fff; z-index: 30; opacity: 0; pointer-events: none; transition: opacity 0.12s ease;"></div>
            </div>

            <!-- BẢNG ĐIỀU KHIỂN DƯỚI CÙNG -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; gap: 10px; flex-wrap: wrap;">
                <!-- Tuỳ chọn Tự động chụp -->
                <div style="display: flex; align-items: center; gap: 6px;">
                    <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none; font-size: 0.88rem; color: var(--text-body); font-weight: 500;">
                        <input type="checkbox" id="auto-capture-toggle" checked style="width: 16px; height: 16px; accent-color: var(--primary); cursor: pointer;">
                        <span style="display: flex; align-items: center; gap: 5px;">
                            <svg class="svg-icon" viewBox="0 0 24 24" style="color: #f59e0b;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                            Tự động chụp khi phát hiện thẻ chuẩn
                        </span>
                    </label>
                </div>

                <!-- Cụm nút thao tác -->
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button type="button" id="btn-switch-camera" class="btn btn-outline" style="padding: 8px 14px; font-size: 0.85rem;" onclick="switchCameraDevice()" title="Đổi camera khác">
                        <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                        Đổi Camera
                    </button>
                    <button type="button" class="btn btn-primary" id="btn-capture-manual" style="padding: 9px 18px; font-weight: 700; font-size: 0.9rem;" onclick="captureSnapshotManual()">
                        <svg class="svg-icon" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                        Chụp Ngay <span style="font-size: 0.72rem; opacity: 0.9; margin-left: 4px; padding: 1px 6px; background: rgba(0,0,0,0.2); border-radius: 3px;">Space</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL XEM CHI TIẾT THẺ CCCD -->
    <div id="modal-view-detail" class="modal">
        <div class="modal-content" style="max-width: 900px; width: 95%; border-radius: 8px; padding: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px;">
                <h3 id="modal-detail-title" style="font-size: 1.25rem; font-weight: 700; color: var(--text-main); letter-spacing: -0.3px; display: flex; align-items: center; gap: 8px;">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="color: var(--primary);"><rect x="2" y="4" width="20" height="16" rx="2"/><circle cx="8" cy="10" r="2.5"/><line x1="13" y1="9" x2="19" y2="9"/><line x1="13" y1="13" x2="19" y2="13"/><line x1="5" y1="16" x2="11" y2="16"/><line x1="14" y1="16" x2="19" y2="16"/></svg>
                    Chi Tiết Thẻ CCCD & Kết Quả Detect
                </h3>
                <button type="button" class="btn btn-outline" style="padding: 4px 10px; border-radius: 4px;" onclick="closeModal('modal-view-detail')">✕</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; align-items: start;">
                <!-- CỘT TRÁI: ẢNH DETECT CỦA THẺ VÀ AVATAR -->
                <div>
                    <h4 style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.4px; display: flex; align-items: center; gap: 6px;">
                        <svg class="svg-icon" viewBox="0 0 24 24" style="color: var(--primary);"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                        Ảnh Thẻ Phát Hiện & Khoanh Vùng Màu
                    </h4>
                    <div style="background: #000; border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center; min-height: 260px;">
                        <img id="detail-card-img" style="width: 100%; max-height: 360px; object-fit: contain;" src="" alt="Ảnh thẻ CCCD">
                    </div>

                    <div id="detail-avatar-box" style="margin-top: 12px; display: flex; align-items: center; gap: 14px; background: #f0f2f5; padding: 12px 14px; border-radius: 6px; border: 1px solid var(--border-color);">
                        <img id="detail-avatar-img" style="width: 58px; height: 74px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color); background: #000;" src="" alt="Avatar">
                        <div>
                            <strong style="font-size: 0.9rem; color: var(--text-main); display: block;">Ảnh chân dung bóc tách</strong>
                            <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; font-weight: 500;">Bóc tách tự động từ Stage 2</p>
                        </div>
                    </div>
                </div>

                <!-- CỘT PHẢI: 8 TRƯỜNG THÔNG TIN TRÍCH XUẤT -->
                <div>
                    <h4 style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.4px; display: flex; align-items: center; gap: 6px;">
                        <svg class="svg-icon" viewBox="0 0 24 24" style="color: var(--success);"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="m9 14 2 2 4-4"/></svg>
                        8 Trường Thông Tin Định Danh
                    </h4>
                    <div style="background: #f0f2f5; border-radius: 6px; border: 1px solid var(--border-color); padding: 14px 16px;">
                        <div class="field-row"><span class="field-title">1. Số CCCD:</span><span class="field-val" id="det-id_number" style="font-size: 1.1rem; color: var(--primary);">---</span></div>
                        <div class="field-row"><span class="field-title">2. Họ và tên:</span><span class="field-val" id="det-full_name" style="font-size: 1rem;">---</span></div>
                        <div class="field-row"><span class="field-title">3. Ngày sinh:</span><span class="field-val" id="det-dob">---</span></div>
                        <div class="field-row"><span class="field-title">4. Giới tính:</span><span class="field-val" id="det-gender">---</span></div>
                        <div class="field-row"><span class="field-title">5. Quốc tịch:</span><span class="field-val" id="det-nationality"><span class="badge badge-success">Việt Nam</span></span></div>
                        <div class="field-row" style="flex-direction: column; align-items: flex-start; gap: 3px;"><span class="field-title">6. Quê quán:</span><span class="field-val" id="det-origin" style="text-align: left; font-size: 0.88rem;">---</span></div>
                        <div class="field-row" style="flex-direction: column; align-items: flex-start; gap: 3px;"><span class="field-title">7. Nơi thường trú:</span><span class="field-val" id="det-residence" style="text-align: left; font-size: 0.88rem;">---</span></div>
                        <div class="field-row"><span class="field-title">8. Có giá trị đến:</span><span class="field-val" id="det-expiry">---</span></div>
                    </div>

                    <div style="margin-top: 14px; display: flex; gap: 8px;">
                        <button type="button" class="btn btn-primary" id="btn-modal-edit" style="flex: 1;" onclick="loadRecordToForm()">
                            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                            Tải vào Form để sửa
                        </button>
                        <button type="button" class="btn btn-outline" onclick="closeModal('modal-view-detail')">Đóng</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TOAST NOTIFICATION -->
    <div id="toast"></div>

    <script>
        let currentScanId = null;
        let currentResultId = null;
        let authToken = localStorage.getItem('token') || '';
        let currentUser = null;
        let activeRecordData = null;

        // ========================================================
        // 1. QUẢN LÝ ĐĂNG NHẬP / ĐĂNG KÝ (AUTH GATEWAY)
        // ========================================================
        function switchAuthTab(type) {
            const alertBox = document.getElementById('auth-alert');
            alertBox.style.display = 'none';
            if (type === 'login') {
                document.getElementById('form-login').style.display = 'block';
                document.getElementById('form-register').style.display = 'none';
                document.getElementById('tab-btn-login').style.background = 'var(--primary)';
                document.getElementById('tab-btn-login').style.color = '#ffffff';
                document.getElementById('tab-btn-register').style.background = 'transparent';
                document.getElementById('tab-btn-register').style.color = 'var(--text-muted)';
            } else {
                document.getElementById('form-login').style.display = 'none';
                document.getElementById('form-register').style.display = 'block';
                document.getElementById('tab-btn-register').style.background = 'var(--primary)';
                document.getElementById('tab-btn-register').style.color = '#ffffff';
                document.getElementById('tab-btn-login').style.background = 'transparent';
                document.getElementById('tab-btn-login').style.color = 'var(--text-muted)';
            }
        }

        function showAuthAlert(msg, isSuccess = false) {
            const box = document.getElementById('auth-alert');
            box.style.display = 'block';
            box.style.background = isSuccess ? 'var(--success-subtle)' : 'var(--danger-subtle)';
            box.style.color = isSuccess ? '#059669' : '#dc2626';
            box.style.border = isSuccess ? '1.5px solid var(--success-border)' : '1.5px solid var(--danger-border)';
            box.innerText = msg;
        }

        async function submitLogin() {
            const u = document.getElementById('login-username').value.trim();
            const p = document.getElementById('login-password').value;
            const btn = document.getElementById('btn-login-submit');
            btn.disabled = true;
            btn.innerText = '⏳ Đang đăng nhập...';

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: u, password: p })
                });
                const data = await res.json();
                if (!res.ok) {
                    showAuthAlert(data.detail || 'Đăng nhập thất bại!');
                    return;
                }

                authToken = data.access_token;
                localStorage.setItem('token', authToken);
                currentUser = data.user;
                onAuthSuccess(data.user);
                showToast('✅ Đăng nhập thành công! Xin chào ' + data.user.full_name);
            } catch (err) {
                showAuthAlert('Lỗi kết nối máy chủ CSDL: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = '🚀 Đăng Nhập';
            }
        }

        async function quickLoginDemo() {
            document.getElementById('login-username').value = 'minh_final';
            document.getElementById('login-password').value = 'password123';
            await submitLogin();
        }

        async function submitRegister() {
            const fullname = document.getElementById('reg-fullname').value.trim();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;
            const btn = document.getElementById('btn-reg-submit');
            btn.disabled = true;
            btn.innerText = '⏳ Đang khởi tạo...';

            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ full_name: fullname, username: username, email: email, password: password })
                });
                const data = await res.json();
                if (!res.ok) {
                    showAuthAlert(data.detail || 'Đăng ký thất bại!');
                    return;
                }

                // Tự động đăng nhập sau khi tạo tài khoản
                document.getElementById('login-username').value = username;
                document.getElementById('login-password').value = password;
                switchAuthTab('login');
                showAuthAlert('Đăng ký thành công! Đang đăng nhập...', true);
                await submitLogin();
            } catch (err) {
                showAuthAlert('Lỗi: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = '✨ Tạo Tài Khoản & Vào Hệ Thống';
            }
        }

        function onAuthSuccess(user) {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-app').style.display = 'block';
            document.getElementById('username-text').innerText = user.full_name;
            const userSub = document.getElementById('user-sub');
            if (userSub) userSub.innerText = '(@' + user.username + ')';

            // Tải dữ liệu ban đầu
            loadResultsList();
            loadStatsAndCorrections();
        }

        function logoutUser(msg = 'Đã đăng xuất khỏi hệ thống!') {
            localStorage.removeItem('token');
            authToken = '';
            currentUser = null;
            document.getElementById('main-app').style.display = 'none';
            document.getElementById('auth-screen').style.display = 'flex';
            document.getElementById('login-password').value = '';
            showAuthAlert(msg, false);
            showToast(msg, false);
        }

        async function initAuth() {
            if (!authToken) {
                document.getElementById('auth-screen').style.display = 'flex';
                document.getElementById('main-app').style.display = 'none';
                return;
            }

            try {
                const res = await fetch('/api/auth/me', {
                    headers: { 'Authorization': 'Bearer ' + authToken }
                });
                if (res.ok) {
                    const user = await res.json();
                    currentUser = user;
                    onAuthSuccess(user);
                } else {
                    logoutUser('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
                }
            } catch (e) {
                document.getElementById('auth-screen').style.display = 'flex';
                document.getElementById('main-app').style.display = 'none';
            }
        }

        function showToast(msg, isSuccess = true) {
            const toast = document.getElementById('toast');
            toast.style.background = isSuccess ? '#059669' : '#dc2626';
            toast.style.color = '#fff';
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');

            if (tabId === 'tab-results') loadResultsList();
            if (tabId === 'tab-stats') loadStatsAndCorrections();
            if (tabId === 'tab-profile') loadUserProfile();
        }

        function loadUserProfile() {
            if (!currentUser) return;
            const u = document.getElementById('prof-username');
            const f = document.getElementById('prof-fullname');
            const e = document.getElementById('prof-email');
            const c = document.getElementById('prof-created');
            if (u) u.value = currentUser.username || '';
            if (f) f.value = currentUser.full_name || '';
            if (e) e.value = currentUser.email || '';
            if (c) c.value = currentUser.created_at ? new Date(currentUser.created_at).toLocaleString('vi-VN') : '---';
        }

        async function submitTabChangePassword() {
            const oldPass = document.getElementById('tab-old-pass').value;
            const newPass = document.getElementById('tab-new-pass').value;
            const confirmPass = document.getElementById('tab-confirm-pass').value;

            if (newPass !== confirmPass) {
                showToast('Mật khẩu mới và xác nhận mật khẩu không khớp!', false);
                return;
            }

            try {
                const res = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify({ old_password: oldPass, new_password: newPass })
                });
                const data = await res.json();
                if (res.ok) {
                    showToast('Đổi mật khẩu thành công!', true);
                    document.getElementById('tab-old-pass').value = '';
                    document.getElementById('tab-new-pass').value = '';
                    document.getElementById('tab-confirm-pass').value = '';
                } else {
                    showToast(data.detail || 'Lỗi khi đổi mật khẩu', false);
                }
            } catch (e) {
                showToast('Lỗi: ' + e.message, false);
            }
        }

        // ========================================================
        // 2A. QUẢN LÝ QUÉT CAMERA THỜI GIAN THỰC & EKYC AUTO-CAPTURE
        // ========================================================
        let cameraStream = null;
        let videoDevices = [];
        let currentCameraIndex = 0;
        let cameraProbeInterval = null;
        let isProbingCamera = false;
        let consecutiveCardHits = 0;
        let isCapturingPhoto = false;
        let lastProbeResult = null;

        async function openCameraModal() {
            const modal = document.getElementById('modal-camera');
            const badgeText = document.getElementById('camera-status-text');
            const badgeDot = document.getElementById('camera-status-dot');

            modal.classList.add('active');
            isCapturingPhoto = false;
            consecutiveCardHits = 0;
            lastProbeResult = null;

            if (badgeText) badgeText.innerText = 'Đang khởi động Camera...';
            if (badgeDot) badgeDot.style.background = '#38bdf8';

            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error('Trình duyệt chưa hỗ trợ Camera hoặc trang web chưa chạy trên localhost / HTTPS!');
                }

                await startCameraStream();

                // Sau khi đã cấp quyền thành công mới liệt kê danh sách camera (để có deviceId chuẩn)
                try {
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    videoDevices = devices.filter(d => d.kind === 'videoinput' && d.deviceId);
                    const btnSwitch = document.getElementById('btn-switch-camera');
                    if (btnSwitch) {
                        btnSwitch.style.display = videoDevices.length > 1 ? 'inline-flex' : 'none';
                    }
                } catch (e) {
                    videoDevices = [];
                }
            } catch (err) {
                console.error('Camera error:', err);
                let friendlyMsg = 'Không thể mở Camera: ' + (err.message || err.name);
                if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                    friendlyMsg = '⚠️ Bạn chưa cho phép trình duyệt dùng Camera! Vui lòng bấm vào biểu tượng 🔒 hoặc biểu tượng Camera trên thanh địa chỉ trình duyệt rồi chọn "Cho phép" (Allow).';
                } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                    friendlyMsg = '⚠️ Camera đang bị ứng dụng khác (Zoom, FaceTime, Meet...) sử dụng. Vui lòng tắt ứng dụng kia rồi thử lại!';
                } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                    friendlyMsg = '⚠️ Không tìm thấy thiết bị Camera nào trên máy tính!';
                } else if (err.name === 'OverconstrainedError') {
                    friendlyMsg = '⚠️ Camera không hỗ trợ độ phân giải yêu cầu. Đang tự động thử lại...';
                }
                showToast(friendlyMsg, false);
                closeCameraModal();
            }
        }

        async function startCameraStream(preferredDeviceId = null) {
            if (cameraStream) {
                cameraStream.getTracks().forEach(t => t.stop());
                cameraStream = null;
            }

            const video = document.getElementById('camera-video');
            let stream = null;

            // Thử lần 1: Yêu cầu độ phân giải và camera mong muốn
            const constraintsTier1 = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            if (preferredDeviceId && typeof preferredDeviceId === 'string' && preferredDeviceId.length > 0) {
                constraintsTier1.video.deviceId = { exact: preferredDeviceId };
            } else {
                constraintsTier1.video.facingMode = { ideal: 'environment' };
            }

            try {
                stream = await navigator.mediaDevices.getUserMedia(constraintsTier1);
            } catch (errTier1) {
                console.warn('Tier 1 constraints failed, trying basic video fallback...', errTier1);
                // Thử lần 2: Fallback về video: true cơ bản nhất (chạy được trên 100% webcam)
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                } catch (errTier2) {
                    console.error('Tier 2 fallback failed:', errTier2);
                    throw errTier2;
                }
            }

            cameraStream = stream;
            video.srcObject = cameraStream;
            await video.play();

            clearInterval(cameraProbeInterval);
            cameraProbeInterval = setInterval(runCameraProbeLoop, 450);
        }

        async function switchCameraDevice() {
            if (videoDevices.length <= 1) return;
            currentCameraIndex = (currentCameraIndex + 1) % videoDevices.length;
            const targetDevice = videoDevices[currentCameraIndex];
            try {
                await startCameraStream(targetDevice.deviceId);
                showToast(`🔄 Đã chuyển sang: ${targetDevice.label || 'Camera ' + (currentCameraIndex + 1)}`, true);
            } catch (e) {
                showToast('Không thể đổi camera: ' + e.message, false);
            }
        }

        function closeCameraModal() {
            const modal = document.getElementById('modal-camera');
            if (modal) modal.classList.remove('active');

            if (cameraProbeInterval) {
                clearInterval(cameraProbeInterval);
                cameraProbeInterval = null;
            }

            if (cameraStream) {
                cameraStream.getTracks().forEach(t => t.stop());
                cameraStream = null;
            }

            const video = document.getElementById('camera-video');
            if (video) video.srcObject = null;

            const countdown = document.getElementById('camera-countdown');
            if (countdown) countdown.style.display = 'none';

            isCapturingPhoto = false;
            isProbingCamera = false;
            consecutiveCardHits = 0;
            clearDetectionBoundingBox();
            resetCameraGuideBoxStyle();
        }

        function clearDetectionBoundingBox() {
            const overlay = document.getElementById('camera-overlay-canvas');
            if (!overlay) return;
            const ctx = overlay.getContext('2d');
            ctx.clearRect(0, 0, overlay.width, overlay.height);
        }

        function drawDetectionBoundingBox(box, color, labelText) {
            const overlay = document.getElementById('camera-overlay-canvas');
            if (!overlay) return;
            const ctx = overlay.getContext('2d');

            const rect = overlay.getBoundingClientRect();
            if (overlay.width !== rect.width || overlay.height !== rect.height) {
                overlay.width = rect.width;
                overlay.height = rect.height;
            }

            ctx.clearRect(0, 0, overlay.width, overlay.height);
            if (!box || box.length < 4) return;

            const x = box[0] * overlay.width;
            const y = box[1] * overlay.height;
            const w = (box[2] - box[0]) * overlay.width;
            const h = (box[3] - box[1]) * overlay.height;

            const hexColor = (color === 'green') ? '#10b981' : (color === 'yellow') ? '#f59e0b' : '#ef4444';
            const bgFill = (color === 'green') ? 'rgba(16, 185, 129, 0.12)' : (color === 'yellow') ? 'rgba(245, 158, 11, 0.12)' : 'rgba(239, 68, 68, 0.18)';

            // 1. Vẽ thân hộp khoanh với viền phát sáng bám theo thẻ
            ctx.fillStyle = bgFill;
            ctx.strokeStyle = hexColor;
            ctx.lineWidth = 3;
            ctx.shadowColor = hexColor;
            ctx.shadowBlur = 14;

            const r = 8;
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.lineTo(x + w - r, y);
            ctx.quadraticCurveTo(x + w, y, x + w, y + r);
            ctx.lineTo(x + w, y + h - r);
            ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
            ctx.lineTo(x + r, y + h);
            ctx.quadraticCurveTo(x, y + h, x, y + h - r);
            ctx.lineTo(x, y + r);
            ctx.quadraticCurveTo(x, y, x + r, y);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // 2. Vẽ 4 góc định vị đậm nét xung quanh thẻ
            ctx.shadowBlur = 0;
            ctx.lineWidth = 5;
            const cLen = Math.min(22, w * 0.2, h * 0.2);

            ctx.beginPath();
            ctx.moveTo(x, y + cLen); ctx.lineTo(x, y); ctx.lineTo(x + cLen, y);
            ctx.moveTo(x + w - cLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cLen);
            ctx.moveTo(x, y + h - cLen); ctx.lineTo(x, y + h); ctx.lineTo(x + cLen, y + h);
            ctx.moveTo(x + w - cLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - cLen);
            ctx.stroke();

            // 3. Nhãn chữ đính kèm ngay trên đầu hộp khoanh
            const shortTag = (color === 'green') ? '🟢 Mặt trước CCCD chuẩn' :
                             (color === 'yellow') ? '⚠️ Mặt sau CCCD (Vui lòng lật lại)' :
                             '❌ Không phải thẻ CCCD';
            ctx.font = 'bold 12px Inter, sans-serif';
            const tm = ctx.measureText(shortTag);
            const tagW = tm.width + 16;
            const tagH = 22;
            const tagX = Math.max(4, Math.min(x, overlay.width - tagW - 4));
            const tagY = (y >= tagH + 6) ? (y - tagH - 6) : (y + 6);

            ctx.fillStyle = hexColor;
            if (ctx.roundRect) {
                ctx.beginPath();
                ctx.roundRect(tagX, tagY, tagW, tagH, 4);
                ctx.fill();
            } else {
                ctx.fillRect(tagX, tagY, tagW, tagH);
            }

            ctx.fillStyle = '#ffffff';
            ctx.fillText(shortTag, tagX + 8, tagY + 15);
        }

        function resetCameraGuideBoxStyle() {
            const box = document.getElementById('camera-guide-box');
            if (box) {
                box.style.border = '2px dashed rgba(255, 255, 255, 0.7)';
                box.style.boxShadow = '0 0 0 9999px rgba(0, 0, 0, 0.5)';
            }
            ['corner-tl', 'corner-tr', 'corner-bl', 'corner-br'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.borderColor = '#38bdf8';
            });
            const badge = document.getElementById('camera-status-badge');
            if (badge) badge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
            const badgeDot = document.getElementById('camera-status-dot');
            if (badgeDot) badgeDot.style.background = '#38bdf8';
            const centerText = document.getElementById('guide-center-text');
            if (centerText) {
                centerText.innerText = 'Đặt mặt trước thẻ CCCD vào khung';
                centerText.style.color = 'rgba(255, 255, 255, 0.75)';
            }
        }

        function setCameraGuideBoxSuccess(msg) {
            const box = document.getElementById('camera-guide-box');
            if (box) {
                box.style.border = '3px solid #10b981';
                box.style.boxShadow = '0 0 25px rgba(16, 185, 129, 0.75), 0 0 0 9999px rgba(0, 0, 0, 0.55)';
            }
            ['corner-tl', 'corner-tr', 'corner-bl', 'corner-br'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.borderColor = '#10b981';
            });
            const badge = document.getElementById('camera-status-badge');
            if (badge) badge.style.borderColor = 'rgba(16, 185, 129, 0.7)';
            const badgeDot = document.getElementById('camera-status-dot');
            if (badgeDot) badgeDot.style.background = '#10b981';
            const centerText = document.getElementById('guide-center-text');
            if (centerText) {
                centerText.innerText = msg || '🟢 Mặt trước CCCD chuẩn! Giữ yên...';
                centerText.style.color = '#10b981';
            }
        }

        function setCameraGuideBoxWarning(msg) {
            const box = document.getElementById('camera-guide-box');
            if (box) {
                box.style.border = '3px solid #f59e0b';
                box.style.boxShadow = '0 0 25px rgba(245, 158, 11, 0.75), 0 0 0 9999px rgba(0, 0, 0, 0.55)';
            }
            ['corner-tl', 'corner-tr', 'corner-bl', 'corner-br'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.borderColor = '#f59e0b';
            });
            const badge = document.getElementById('camera-status-badge');
            if (badge) badge.style.borderColor = 'rgba(245, 158, 11, 0.7)';
            const badgeDot = document.getElementById('camera-status-dot');
            if (badgeDot) badgeDot.style.background = '#f59e0b';
            const centerText = document.getElementById('guide-center-text');
            if (centerText) {
                centerText.innerText = msg || '⚠️ Đây là MẶT SAU CCCD! Vui lòng lật lại mặt trước';
                centerText.style.color = '#f59e0b';
            }
        }

        function setCameraGuideBoxDanger(msg) {
            const box = document.getElementById('camera-guide-box');
            if (box) {
                box.style.border = '3px solid #ef4444';
                box.style.boxShadow = '0 0 25px rgba(239, 68, 68, 0.85), 0 0 0 9999px rgba(0, 0, 0, 0.55)';
            }
            ['corner-tl', 'corner-tr', 'corner-bl', 'corner-br'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.borderColor = '#ef4444';
            });
            const badge = document.getElementById('camera-status-badge');
            if (badge) badge.style.borderColor = 'rgba(239, 68, 68, 0.7)';
            const badgeDot = document.getElementById('camera-status-dot');
            if (badgeDot) badgeDot.style.background = '#ef4444';
            const centerText = document.getElementById('guide-center-text');
            if (centerText) {
                centerText.innerText = msg || '❌ Không phải thẻ CCCD! Vui lòng đưa đúng thẻ CCCD';
                centerText.style.color = '#ef4444';
            }
        }

        // LẮNG NGHE PHÍM SPACE ĐỂ CHỤP THỦ CÔNG
        window.addEventListener('keydown', (e) => {
            const modal = document.getElementById('modal-camera');
            if (modal && modal.classList.contains('active')) {
                if (e.code === 'Space' || e.key === ' ') {
                    const tag = (e.target && e.target.tagName) ? e.target.tagName.toUpperCase() : '';
                    if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
                        e.preventDefault();
                        captureSnapshotManual();
                    }
                } else if (e.key === 'Escape') {
                    closeCameraModal();
                }
            }
        });

        // LUỒNG THĂM DÒ NHẬN DIỆN THẺ (PROBE LOOP)
        async function runCameraProbeLoop() {
            if (isCapturingPhoto || isProbingCamera) return;
            const modal = document.getElementById('modal-camera');
            if (!modal || !modal.classList.contains('active')) return;

            const video = document.getElementById('camera-video');
            if (!video || video.readyState < 2 || !video.videoWidth) return;

            isProbingCamera = true;
            try {
                const canvas = document.getElementById('camera-canvas');
                const scale = Math.min(1.0, 640 / video.videoWidth);
                canvas.width = Math.round(video.videoWidth * scale);
                canvas.height = Math.round(video.videoHeight * scale);
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.75));
                if (!blob) { isProbingCamera = false; return; }

                const formData = new FormData();
                formData.append('file', blob, 'probe.jpg');

                const res = await fetch('/predict/camera-probe', { method: 'POST', body: formData });
                if (!res.ok) { isProbingCamera = false; return; }
                const data = await res.json();
                lastProbeResult = data;

                const badgeText = document.getElementById('camera-status-text');
                if (badgeText) badgeText.innerText = data.message || 'Đang quét...';

                // Vẽ khung khoanh trực tiếp trên vị trí thẻ (nếu phát hiện thẻ)
                if (data.box && data.box.length === 4) {
                    drawDetectionBoundingBox(data.box, data.color, data.message);
                } else {
                    clearDetectionBoundingBox();
                }

                if (data.detected && data.color === 'green' && data.side === 'front') {
                    consecutiveCardHits++;
                    setCameraGuideBoxSuccess(data.message);

                    const autoToggle = document.getElementById('auto-capture-toggle');
                    const isAutoEnabled = autoToggle ? autoToggle.checked : true;

                    if (isAutoEnabled && consecutiveCardHits >= 2 && !isCapturingPhoto) {
                        triggerAutoCapture();
                    }
                } else {
                    consecutiveCardHits = 0;
                    if (data.color === 'red') {
                        setCameraGuideBoxDanger(data.message);
                    } else if (data.color === 'yellow') {
                        setCameraGuideBoxWarning(data.message);
                    } else {
                        resetCameraGuideBoxStyle();
                    }
                }
            } catch (e) {
                // Ignore probe error
            } finally {
                isProbingCamera = false;
            }
        }

        // TỰ ĐỘNG CHỤP VỚI ĐẾM NGƯỢC
        function triggerAutoCapture() {
            if (isCapturingPhoto) return;
            isCapturingPhoto = true;

            const countdownOverlay = document.getElementById('camera-countdown');
            const countdownNum = document.getElementById('countdown-number');
            if (countdownOverlay) countdownOverlay.style.display = 'flex';
            if (countdownNum) countdownNum.innerText = '1';

            setTimeout(() => {
                executeCaptureFrame('📸 Tự động chụp (Phát hiện thẻ chuẩn)');
            }, 500);
        }

        // BẤM NÚT CHỤP THỦ CÔNG HOẶC PHÍM SPACE
        function captureSnapshotManual() {
            if (isCapturingPhoto) return;
            // Kiểm tra nghiêm ngặt: Phải đúng là thẻ CCCD chuẩn (màu xanh) mới cho phép chụp
            if (!lastProbeResult || !lastProbeResult.detected || lastProbeResult.color !== 'green') {
                const msg = (lastProbeResult && lastProbeResult.message) ? lastProbeResult.message : 'Chưa nhận diện được mặt trước thẻ CCCD!';
                showToast(`⚠️ Không thể chụp: ${msg}`, false);
                return;
            }
            isCapturingPhoto = true;
            executeCaptureFrame('📸 Chụp thủ công');
        }

        // CHỤP FRAME GỐC VÀ GỬI TỚI AI PIPELINE
        function executeCaptureFrame(sourceDesc) {
            const video = document.getElementById('camera-video');
            const flash = document.getElementById('camera-flash');
            const canvas = document.getElementById('camera-canvas');

            if (flash) {
                flash.style.display = 'block';
                flash.style.opacity = '0.9';
                setTimeout(() => {
                    flash.style.opacity = '0';
                    setTimeout(() => { flash.style.display = 'none'; }, 150);
                }, 100);
            }

            canvas.width = video.videoWidth || 1920;
            canvas.height = video.videoHeight || 1080;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(blob => {
                closeCameraModal();
                if (blob) {
                    showToast(`${sourceDesc}! Đang gửi AI trích xuất...`, true);
                    processImageFile(blob, true);
                } else {
                    showToast('Lỗi khi chụp khung hình!', false);
                }
            }, 'image/jpeg', 0.95);
        }

        // ========================================================
        // 2B. XỬ LÝ ẢNH (DÙNG CHUNG CHO CẢ TẢI FILE VÀ CHỤP CAMERA)
        // ========================================================
        function uploadImage(e) {
            const file = e.target.files[0];
            if (!file) return;
            processImageFile(file, false);
        }

        async function processImageFile(fileOrBlob, isCamera = false) {
            const preview = document.getElementById('preview');
            const status = document.getElementById('status');
            const btnSave = document.getElementById('btn-save');
            const sourceBadge = document.getElementById('source-badge');

            if (sourceBadge) {
                sourceBadge.innerText = isCamera ? '🎥 Camera' : '📁 File ảnh';
                sourceBadge.className = 'badge badge-success';
            }

            preview.src = URL.createObjectURL(fileOrBlob);
            preview.style.display = 'block';

            status.className = 'status loading';
            status.innerText = isCamera 
                ? '⏳ [Camera] Đang xoay nắn 360°, bóc tách 8 vùng & nhận diện VietOCR...' 
                : '⏳ Đang xoay nắn 360°, bóc tách 8 vùng & nhận diện VietOCR...';
            btnSave.disabled = true;

            const formData = new FormData();
            const fileName = isCamera ? 'camera_capture.jpg' : (fileOrBlob.name || 'cccd_upload.jpg');
            formData.append('file', fileOrBlob, fileName);

            const headers = {};
            if (authToken) headers['Authorization'] = 'Bearer ' + authToken;

            try {
                const res = await fetch('/predict/image', { method: 'POST', headers: headers, body: formData });
                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                const data = await res.json();

                if (!res.ok || data.error) {
                    status.className = 'status error';
                    status.innerText = '❌ ' + (data.error || 'Nhận diện thất bại!');
                    showToast('❌ ' + (data.error || 'Nhận diện thất bại!'), false);
                    btnSave.disabled = true;
                    document.getElementById('val-so_cccd').value = '';
                    document.getElementById('val-ho_ten').value = '';
                    document.getElementById('val-ngay_sinh').value = '';
                    document.getElementById('val-gioi_tinh').value = '';
                    document.getElementById('val-quoc_tich').value = 'Việt Nam';
                    document.getElementById('val-que_quan').value = '';
                    document.getElementById('val-noi_ctru').value = '';
                    document.getElementById('val-ngay_het_han').value = '';
                    currentScanId = null;
                    currentResultId = null;
                    return;
                }

                if (data.visualization_base64) {
                    preview.src = data.visualization_base64;
                    preview.style.display = 'block';
                }

                document.getElementById('val-so_cccd').value = data.so_cccd || '';
                document.getElementById('val-ho_ten').value = data.ho_ten || '';
                document.getElementById('val-ngay_sinh').value = data.ngay_sinh || '';
                document.getElementById('val-gioi_tinh').value = data.gioi_tinh || '';
                document.getElementById('val-quoc_tich').value = data.quoc_tich || 'Việt Nam';
                document.getElementById('val-que_quan').value = data.que_quan || '';
                document.getElementById('val-noi_ctru').value = data.noi_ctru || '';
                document.getElementById('val-ngay_het_han').value = data.ngay_het_han || '';

                currentScanId = data.scan_id;
                currentResultId = data.result_id;
                btnSave.disabled = false;

                status.className = 'status success';
                status.innerText = '✅ Nhận diện thành công! Đã khoanh vùng 8 trường và lưu vào CSDL.';
                showToast('✅ Đã nhận diện và lưu hồ sơ thành công!', true);
            } catch (err) {
                status.className = 'status error';
                status.innerText = '❌ Lỗi kết nối: ' + err.message;
            }
        }

        // ========================================================
        // 3. CHỈNH SỬA VÀ LƯU VÀO CSDL (GHI NHẬN ĐỘ ĐÚNG AI)
        // ========================================================
        async function saveEditedResult() {
            if (!currentResultId) {
                showToast('Chưa có hồ sơ nào được quét!', false);
                return;
            }

            const payload = {
                id_number: document.getElementById('val-so_cccd').value.trim(),
                full_name: document.getElementById('val-ho_ten').value.trim(),
                dob: formatDateForApi(document.getElementById('val-ngay_sinh').value.trim()),
                gender: document.getElementById('val-gioi_tinh').value.trim(),
                nationality: document.getElementById('val-quoc_tich').value.trim(),
                origin_location: document.getElementById('val-que_quan').value.trim(),
                residence: document.getElementById('val-noi_ctru').value.trim(),
                expiry_date: formatDateForApi(document.getElementById('val-ngay_het_han').value.trim())
            };

            try {
                const res = await fetch(`/api/results/${currentResultId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify(payload)
                });

                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }

                if (res.ok) {
                    showToast('✅ Đã lưu chỉnh sửa vào CSDL và ghi nhận độ đúng của AI!');
                    const status = document.getElementById('status');
                    status.className = 'status success';
                    status.innerText = '✅ Hồ sơ đã được cập nhật chính thức vào CSDL (Bảng cccd_results).';
                } else {
                    const err = await res.json();
                    showToast('❌ Lỗi cập nhật: ' + (err.detail || 'Thất bại'), false);
                }
            } catch (e) {
                showToast('❌ Lỗi kết nối server: ' + e.message, false);
            }
        }

        function formatDateForApi(dStr) {
            if (!dStr) return null;
            const parts = dStr.split(/[\/\-]/);
            if (parts.length === 3) {
                if (parts[0].length === 2 && parts[2].length === 4) {
                    return `${parts[2]}-${parts[1]}-${parts[0]}`;
                }
            }
            return dStr;
        }

        // ========================================================
        // 4. TẢI DANH SÁCH BẢNG LƯU KẾT QUẢ (cccd_results)
        // ========================================================
        async function loadResultsList() {
            const tbody = document.getElementById('results-tbody');
            const search = document.getElementById('search-input').value.trim();
            const url = '/api/results' + (search ? `?search=${encodeURIComponent(search)}` : '');

            try {
                const res = await fetch(url, { headers: { 'Authorization': 'Bearer ' + authToken } });
                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                const data = await res.json();

                if (!data.items || data.items.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="12" style="text-align:center; color:var(--text-muted);">Không có hồ sơ nào phù hợp.</td></tr>';
                    return;
                }

                tbody.innerHTML = data.items.map(r => `
                    <tr>
                        <td><strong>#${r.id}</strong></td>
                        <td style="text-align:center;">
                            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.8rem; color: var(--primary); border-color: rgba(56, 189, 248, 0.4);" 
                                    onclick="viewResultDetail(${r.id})" title="Bấm để xem ảnh detect và các trường">
                                <svg class="svg-icon" viewBox="0 0 24 24" style="width:14px; height:14px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg> Xem thẻ
                            </button>
                        </td>
                        <td style="color:var(--primary); font-weight:700;">${r.id_number}</td>
                        <td style="font-weight:700;">${r.full_name}</td>
                        <td>${r.dob || '---'}</td>
                        <td>${r.gender || '---'}</td>
                        <td><span class="badge badge-success">${r.nationality || 'Việt Nam'}</span></td>
                        <td style="max-width:180px;" title="${r.origin_location}">${r.origin_location || '---'}</td>
                        <td style="max-width:200px;" title="${r.residence}">${r.residence || '---'}</td>
                        <td>${r.expiry_date || '---'}</td>
                        <td style="color:var(--text-muted); font-size:0.8rem;">${new Date(r.saved_at).toLocaleString('vi-VN')}</td>
                        <td style="text-align:center;">
                            <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.85rem; color: #ef4444; border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.08);" 
                                    onclick="deleteResultRecord(${r.id})" title="Xóa kết quả này khỏi hệ thống">
                                <svg class="svg-icon" viewBox="0 0 24 24" style="width:14px; height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg> Xóa
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (e) {
                tbody.innerHTML = `<tr><td colspan="12" style="color:red; text-align:center;">Lỗi tải dữ liệu: ${e.message}</td></tr>`;
            }
        }

        async function deleteResultRecord(resultId) {
            if (!confirm(`Bạn có chắc chắn muốn xóa hồ sơ CCCD #${resultId} khỏi hệ thống không?\nThao tác này sẽ xóa vĩnh viễn kết quả và lịch sử quét liên quan.`)) {
                return;
            }
            try {
                const res = await fetch(`/api/results/${resultId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer ' + authToken }
                });
                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                if (res.ok) {
                    showToast(`Đã xóa thành công hồ sơ CCCD #${resultId}!`, true);
                    loadResultsList();
                    loadStatsAndCorrections();
                } else {
                    const err = await res.json();
                    showToast(err.detail || 'Lỗi khi xóa kết quả!', false);
                }
            } catch (e) {
                showToast('Lỗi khi xóa: ' + e.message, false);
            }
        }

        async function viewResultDetail(resultId) {
            try {
                const res = await fetch(`/api/results/${resultId}`, {
                    headers: { 'Authorization': 'Bearer ' + authToken }
                });
                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                if (!res.ok) {
                    showToast('Không thể tải chi tiết thẻ!', false);
                    return;
                }
                const data = await res.json();
                activeRecordData = data;

                document.getElementById('modal-detail-title').innerText = `🪪 Chi Tiết Thẻ CCCD & Kết Quả Detect (Hồ Sơ #${data.id})`;

                // 1. Cập nhật ảnh detect có khung màu
                const cardImg = document.getElementById('detail-card-img');
                const imgPath = data.crop_image_path || '/media/cccd_fields_visualization.jpg';
                cardImg.src = imgPath + '?t=' + new Date().getTime();

                // 2. Cập nhật ảnh avatar nếu có
                const avatarBox = document.getElementById('detail-avatar-box');
                const avatarImg = document.getElementById('detail-avatar-img');
                if (data.avatar_path) {
                    avatarImg.src = data.avatar_path + '?t=' + new Date().getTime();
                    avatarBox.style.display = 'flex';
                } else {
                    avatarBox.style.display = 'none';
                }

                // 3. Đổ 8 trường vào modal
                document.getElementById('det-id_number').innerText = data.id_number || '---';
                document.getElementById('det-full_name').innerText = data.full_name || '---';
                document.getElementById('det-dob').innerText = data.dob || '---';
                document.getElementById('det-gender').innerText = data.gender || '---';
                document.getElementById('det-nationality').innerText = data.nationality || 'Việt Nam';
                document.getElementById('det-origin').innerText = data.origin_location || '---';
                document.getElementById('det-residence').innerText = data.residence || '---';
                document.getElementById('det-expiry').innerText = data.expiry_date || '---';

                openModal('modal-view-detail');
            } catch (err) {
                showToast('Lỗi: ' + err.message, false);
            }
        }

        function loadRecordToForm() {
            if (!activeRecordData) return;
            const data = activeRecordData;

            // Đổ vào Tab 1 form để người dùng xem và chỉnh sửa
            document.getElementById('val-so_cccd').value = data.id_number || '';
            document.getElementById('val-ho_ten').value = data.full_name || '';
            document.getElementById('val-ngay_sinh').value = data.dob || '';
            document.getElementById('val-gioi_tinh').value = data.gender || '';
            document.getElementById('val-quoc_tich').value = data.nationality || 'Việt Nam';
            document.getElementById('val-que_quan').value = data.origin_location || '';
            document.getElementById('val-noi_ctru').value = data.residence || '';
            document.getElementById('val-ngay_het_han').value = data.expiry_date || '';

            // Cập nhật ảnh preview ở Tab 1
            const preview = document.getElementById('preview');
            const imgPath = data.crop_image_path || '/media/cccd_fields_visualization.jpg';
            preview.src = imgPath + '?t=' + new Date().getTime();
            preview.style.display = 'block';

            currentResultId = data.id;
            currentScanId = data.history_id;
            document.getElementById('btn-save').disabled = false;

            closeModal('modal-view-detail');
            switchTab('tab-scan');
            showToast('✅ Đã tải thông tin vào Form. Bạn có thể chỉnh sửa và bấm Lưu!');
        }

        // ========================================================
        // 5. TẢI THỐNG KÊ & BẢNG ĐỘ ĐÚNG AI (scan_statistics & ai_corrections)
        // ========================================================
        async function loadStatsAndCorrections() {
            try {
                // Tải thống kê
                const resStat = await fetch('/api/statistics', { headers: { 'Authorization': 'Bearer ' + authToken } });
                if (resStat.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                if (resStat.ok) {
                    const st = await resStat.json();
                    document.getElementById('stat-total').innerText = st.total_scans;
                    document.getElementById('stat-sources').innerText = `${st.image_scans} / ${st.webcam_scans} / ${st.video_scans}`;
                    document.getElementById('stat-edited').innerText = st.edited_scans;
                    document.getElementById('stat-confidence').innerText = st.avg_confidence + '%';
                }

                // Tải bảng ai_corrections
                const resCorr = await fetch('/api/corrections', { headers: { 'Authorization': 'Bearer ' + authToken } });
                const tbody = document.getElementById('corrections-tbody');
                if (resCorr.ok) {
                    const list = await resCorr.json();
                    if (list.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">Chưa có lượt sửa nào. Mô hình AI nhận diện chính xác 100%.</td></tr>';
                        return;
                    }
                    tbody.innerHTML = list.map(c => `
                        <tr>
                            <td>#${c.history_id}</td>
                            <td><strong style="color:#a5b4fc;">${c.field_name}</strong></td>
                            <td style="color:#f87171; text-decoration:line-through;">${c.ai_prediction || '(Rỗng)'}</td>
                            <td style="color:#34d399; font-weight:700;">${c.user_corrected}</td>
                            <td><span class="badge badge-warning">AI sai - Người dùng đã sửa</span></td>
                            <td>${c.ai_confidence ? Math.round(c.ai_confidence * 100) + '%' : '---'}</td>
                            <td style="color:var(--text-muted); font-size:0.8rem;">${new Date(c.corrected_at).toLocaleString('vi-VN')}</td>
                        </tr>
                    `).join('');
                }
            } catch (e) { console.log(e); }
        }

        // ========================================================
        // 6. TIỆN ÍCH MODAL & ĐỔI MẬT KHẨU
        // ========================================================
        function openModal(id) { document.getElementById(id).classList.add('active'); }
        function closeModal(id) { document.getElementById(id).classList.remove('active'); }

        async function submitChangePassword() {
            const old_password = document.getElementById('old-pass').value;
            const new_password = document.getElementById('new-pass').value;
            try {
                const res = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken },
                    body: JSON.stringify({ old_password, new_password })
                });
                if (res.status === 401) {
                    logoutUser('Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.');
                    return;
                }
                if (res.ok) {
                    showToast('✅ Đổi mật khẩu thành công!');
                    closeModal('modal-password');
                    document.getElementById('old-pass').value = '';
                    document.getElementById('new-pass').value = '';
                } else {
                    const err = await res.json();
                    showToast('❌ ' + (err.detail || 'Đổi mật khẩu thất bại'), false);
                }
            } catch (e) { showToast('❌ Lỗi kết nối: ' + e.message, false); }
        }

        // Tự động kiểm tra trạng thái đăng nhập khi vừa mở trang web
        window.addEventListener('DOMContentLoaded', initAuth);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_UI


@app.post("/predict/camera-probe", summary="Thăm dò camera thời gian thực để hỗ trợ tự động chụp eKYC")
async def camera_probe_api(file: UploadFile = File(...)):
    import cv2
    import numpy as np

    contents = await file.read()
    if not contents:
        return {"detected": False, "score": 0.0, "message": "Khung hình rỗng", "color": "white", "box": None}

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"detected": False, "score": 0.0, "message": "Lỗi đọc ảnh", "color": "white", "box": None}

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Kiểm tra độ sáng trung bình
    mean_brightness = float(np.mean(gray))
    if mean_brightness < 32:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá tối! Vui lòng tăng sáng", "color": "yellow", "box": None}
    if mean_brightness > 240:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá lóa sáng! Tránh nguồn sáng chói", "color": "yellow", "box": None}

    # 2. Kiểm tra độ sắc nét
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < 24.0:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Ảnh bị rung/mờ! Vui lòng giữ yên", "color": "yellow", "box": None}

    # 3. Sử dụng mô hình YOLO Stage 1 + Stage 2 và VietOCR theo đúng trọng số pipeline
    try:
        from src.detectors.card_detector import _load_model
        from src.detectors.field_detector import field_model, extract_fields_yolo
        from src.ocr.ocr_engine import read_field
        from src.core.validator import clean_id_number

        card_model = _load_model()
        results = card_model.predict(img, conf=0.18, verbose=False, imgsz=640)

        best_box = None
        best_conf = 0.0
        best_cls = -1

        for r in results:
            for b in r.boxes:
                c = float(b.conf[0])
                if c > best_conf:
                    best_conf = c
                    best_box = b
                    best_cls = int(b.cls[0])

        if best_box is not None and best_conf >= 0.18:
            xyxy = best_box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = max(0, xyxy[0]), max(0, xyxy[1]), min(w, xyxy[2]), min(h, xyxy[3])
            norm_box = [round(float(x1) / w, 3), round(float(y1) / h, 3), round(float(x2) / w, 3), round(float(y2) / h, 3)]
            bw = x2 - x1
            bh = y2 - y1
            area_ratio = (bw * bh) / (w * h)

            # Trường hợp 1: Phát hiện MẶT SAU CCCD (Class 0: back-cccd)
            if best_cls == 0:
                return {
                    "detected": False,
                    "side": "back",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "⚠️ Đây là MẶT SAU CCCD! Vui lòng lật lại mặt trước",
                    "color": "yellow"
                }

            # Kiểm tra cự ly thẻ
            if area_ratio < 0.08:
                return {
                    "detected": False,
                    "side": "front_far",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "📏 Đưa thẻ CCCD lại gần camera hơn",
                    "color": "yellow"
                }

            # Trường hợp 2: Kiểm tra tỷ lệ khung thẻ (Aspect Ratio của CCCD ~ 1.58)
            ar = bw / max(1.0, bh)
            if ar < 1.15 or ar > 2.3:
                return {
                    "detected": False,
                    "side": "invalid_card",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "❌ Không phải thẻ CCCD! (Sai tỷ lệ khung thẻ)",
                    "color": "red"
                }

            # Trường hợp 3: Xác thực bằng Stage 2 (extract_fields_yolo giống hệt upload pipeline)
            crop = img[y1:y2, x1:x2]
            if crop.size > 0:
                fields = extract_fields_yolo(crop)
                has_key_fields = ('so_cccd' in fields or 'ho_ten' in fields)
                if not fields or len(fields) < 2 or not has_key_fields:
                    return {
                        "detected": False,
                        "side": "invalid_card",
                        "box": norm_box,
                        "score": round(best_conf, 2),
                        "message": "❌ Không phải thẻ CCCD! (Phát hiện thẻ sinh viên / thẻ khác)",
                        "color": "red"
                    }

                # Đọc kiểm tra số CCCD bằng VietOCR (chuẩn 12 chữ số như upload pipeline)
                if 'so_cccd' in fields:
                    id_res = read_field('so_cccd', fields['so_cccd'])
                    digits = clean_id_number(id_res.get('text', ''))
                    if digits:
                        if len(digits) == 12:
                            return {
                                "detected": True,
                                "side": "front",
                                "box": norm_box,
                                "score": round(best_conf, 2),
                                "message": f"🟢 Thẻ CCCD chuẩn 12 số ({digits[:4]}****{digits[-3:]})! Giữ yên...",
                                "color": "green"
                            }
                        else:
                            # Thẻ sinh viên có 7-8 số, thẻ ATM có 16 số -> Không phải CCCD
                            return {
                                "detected": False,
                                "side": "invalid_card",
                                "box": norm_box,
                                "score": round(best_conf, 2),
                                "message": f"❌ Không phải thẻ CCCD! (Số thẻ {digits} không phải 12 số CCCD)",
                                "color": "red"
                            }

                # Nếu có từ 4 trường thông tin CCCD trở lên gồm cả họ tên và ngày sinh
                if len(fields) >= 4 and 'ho_ten' in fields and 'ngay_sinh' in fields:
                    return {
                        "detected": True,
                        "side": "front",
                        "box": norm_box,
                        "score": round(best_conf, 2),
                        "message": f"🟢 Mặt trước CCCD chuẩn ({len(fields)} trường)! Giữ yên...",
                        "color": "green"
                    }

                return {
                    "detected": False,
                    "side": "front_checking",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "🔍 Đang xác thực thẻ CCCD... Giữ yên thẻ",
                    "color": "red"
                }

        # Nếu Stage 1 không thấy CCCD, kiểm tra xem có vật thể/thẻ khác trong khung hình không
        has_card_shape = False
        best_contour = None
        best_area = 0.0
        total_area = float(w * h)

        for thresh_type in [cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV]:
            _, thresh = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                area = cv2.contourArea(c)
                ratio = area / total_area
                if 0.08 <= ratio <= 0.95 and area > best_area:
                    rect = cv2.minAreaRect(c)
                    rw, rh = rect[1]
                    if rw > 0 and rh > 0:
                        ar = max(rw, rh) / min(rw, rh)
                        if 1.15 <= ar <= 2.4:
                            has_card_shape = True
                            best_area = area
                            best_contour = c

        if has_card_shape and best_contour is not None:
            cx, cy, cw_c, ch_c = cv2.boundingRect(best_contour)
            box_candidate = [round(float(cx) / w, 3), round(float(cy) / h, 3), round(float(cx + cw_c) / w, 3), round(float(cy + ch_c) / h, 3)]
            return {
                "detected": False,
                "side": "invalid_card",
                "box": box_candidate,
                "score": 0.0,
                "message": "❌ Không phải thẻ CCCD! (Phát hiện thẻ sinh viên / thẻ khác)",
                "color": "red"
            }

    except Exception as e:
        import traceback
        print("Lỗi camera_probe_api:", e)
        traceback.print_exc()

    return {
        "detected": False,
        "side": "none",
        "box": None,
        "score": 0.0,
        "message": "🔍 Đặt mặt trước thẻ CCCD vào khung",
        "color": "white"
    }


@app.post("/predict/image", summary="Trích xuất thông tin CCCD từ file ảnh")
async def predict_api(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ("jpg", "jpeg", "png", "bmp", "webp"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh định dạng JPG, JPEG, PNG, BMP hoặc WEBP!")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File ảnh rỗng!")

    try:
        temp_dir = Path("data/input")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"upload_{file.filename}"

        with open(temp_path, "wb") as f:
            f.write(contents)

        try:
            result = process_cccd(temp_path)
        except ValueError as ve:
            return JSONResponse(
                status_code=400,
                content={"error": str(ve)}
            )
        except Exception as ex:
            return JSONResponse(
                status_code=422,
                content={"error": f"Lỗi xử lý: {str(ex)}"}
            )
        finally:
            if temp_path.exists():
                temp_path.unlink()

        if not result:
            return JSONResponse(
                status_code=422,
                content={"error": "Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất."}
            )

        # 1. Nạp ảnh vẽ 8 khung bounding box màu sắc và chuyển sang dạng Base64
        viz_path = Path("data/output/cccd_fields_visualization.jpg")
        if viz_path.exists():
            with open(viz_path, "rb") as f:
                encoded_img = base64.b64encode(f.read()).decode('utf-8')
                result["visualization_base64"] = f"data:image/jpeg;base64,{encoded_img}"

        # 2. Tự động lưu vào PostgreSQL (lưu vào scan_history & cccd_results đủ 8 trường)
        try:
            from src.database.connection import SessionLocal
            from src.database.crud import create_scan_and_save_result
            from src.database.models import User
            from src.database.security import decode_token

            db_session = SessionLocal()
            try:
                user = None
                if authorization and authorization.startswith("Bearer "):
                    token_str = authorization.split(" ")[1]
                    try:
                        payload = decode_token(token_str)
                        uid = int(payload.get("sub"))
                        user = db_session.query(User).filter(User.id == uid).first()
                    except Exception:
                        pass

                if not user:
                    user = db_session.query(User).first()

                if user:
                    extracted = {
                        "id": result.get("so_cccd"),
                        "name": result.get("ho_ten"),
                        "dob": result.get("ngay_sinh"),
                        "gender": result.get("gioi_tinh"),
                        "nationality": result.get("quoc_tich", "Việt Nam"),
                        "origin_place": result.get("que_quan"),
                        "current_place": result.get("noi_ctru"),
                        "expire_date": result.get("ngay_het_han")
                    }
                    file_stem = Path(file.filename).stem
                    upload_stem = f"upload_{file_stem}"
                    import shutil

                    # Lưu ảnh detect phân vùng màu sắc theo scan riêng biệt
                    viz_save_path = Path("data/output/cards") / f"{upload_stem}_viz.jpg"
                    if viz_path.exists():
                        try:
                            shutil.copy(viz_path, viz_save_path)
                            crop_path_val = f"/media/cards/{upload_stem}_viz.jpg"
                        except Exception:
                            crop_path_val = "/media/cccd_fields_visualization.jpg"
                    elif (Path("data/output/cards") / f"{upload_stem}_enhanced.jpg").exists():
                        crop_path_val = f"/media/cards/{upload_stem}_enhanced.jpg"
                    else:
                        crop_path_val = "/media/cccd_fields_visualization.jpg"

                    avatar_file = Path("data/output/avatars") / f"{upload_stem}_avatar.jpg"
                    avatar_path_val = f"/media/avatars/{upload_stem}_avatar.jpg" if avatar_file.exists() else None

                    scan_obj, res_obj = create_scan_and_save_result(
                        db=db_session,
                        user_id=user.id,
                        extracted_fields=extracted,
                        input_source="IMAGE",
                        raw_image_path=crop_path_val,
                        crop_image_path=crop_path_val,
                        avatar_path=avatar_path_val,
                        confidence_score=0.96,
                        processing_time=0.15
                    )
                    result["scan_id"] = scan_obj.id
                    result["result_id"] = res_obj.id
                    result["crop_image_path"] = crop_path_val
                    result["avatar_path"] = avatar_path_val
            finally:
                db_session.close()
        except Exception as db_err:
            print(f"[DB Warning] Lưu kết quả vào CSDL thất bại: {db_err}")

        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi xử lý server: {str(e)}"}
        )


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)