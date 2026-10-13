-- ==============================================================================
-- CƠ SỞ DỮ LIỆU HỆ THỐNG AI NHẬN DIỆN CCCD (NHÓM 10 - 74DCTT24)
-- 1. users: Quản lý tài khoản
-- 2. scan_history: Quản lý lịch sử các lần quét
-- 3. cccd_results: BẢNG LƯU KẾT QUẢ TRÍCH XUẤT ĐỦ 8 TRƯỜNG CCCD
-- 4. scan_statistics: Quản lý thống kê hệ thống
-- 5. ai_corrections: Phân chia độ đúng của AI và người dùng đã sửa gì
-- ==============================================================================

-- 1. BẢNG TÀI KHOẢN NGƯỜI DÙNG
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. BẢNG LỊCH SỬ CÁC LẦN QUÉT
CREATE TABLE IF NOT EXISTS scan_history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_image_path TEXT,                       -- Ảnh gốc / video tải lên
    crop_image_path TEXT,                      -- Ảnh thẻ nắn phẳng 860x542
    avatar_path TEXT,                          -- Ảnh chân dung cắt riêng
    input_source VARCHAR(20) DEFAULT 'IMAGE',  -- IMAGE, WEBCAM, VIDEO
    status VARCHAR(50) DEFAULT 'COMPLETED',    -- COMPLETED, EDITED
    confidence_score FLOAT,                    -- Độ tin cậy trung bình của AI
    processing_time FLOAT,                     -- Thời gian xử lý (giây)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BẢNG LƯU KẾT QUẢ CCCD CHÍNH THỨC (ĐỦ 8 TRƯỜNG DỮ LIỆU ĐỊNH DANH)
CREATE TABLE IF NOT EXISTS cccd_results (
    id SERIAL PRIMARY KEY,
    history_id INT NOT NULL UNIQUE REFERENCES scan_history(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- ĐỦ 8 TRƯỜNG THÔNG TIN MẶT TRƯỚC CCCD:
    id_number VARCHAR(12) NOT NULL,            -- Trường 1: Số CCCD (12 chữ số)
    full_name VARCHAR(100) NOT NULL,           -- Trường 2: Họ và tên
    dob DATE,                                  -- Trường 3: Ngày, tháng, năm sinh
    gender VARCHAR(10),                        -- Trường 4: Giới tính (Nam / Nữ)
    nationality VARCHAR(50) DEFAULT 'Việt Nam',-- Trường 5: Quốc tịch (Việt Nam)
    origin_location TEXT,                      -- Trường 6: Quê quán
    residence TEXT,                            -- Trường 7: Nơi thường trú
    expiry_date DATE,                          -- Trường 8: Có giá trị đến
    
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. BẢNG THỐNG KÊ HỆ THỐNG
CREATE TABLE IF NOT EXISTS scan_statistics (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    total_scans INT DEFAULT 0,                 -- Tổng lượt quét
    image_scans INT DEFAULT 0,                 -- Quét bằng ảnh tải lên
    webcam_scans INT DEFAULT 0,                -- Quét bằng webcam/chụp trực tiếp
    video_scans INT DEFAULT 0,                 -- Quét bằng video tải lên
    edited_scans INT DEFAULT 0,                -- Số lượt phải chỉnh sửa do AI đọc sai
    avg_confidence FLOAT DEFAULT 0.0,          -- Độ tin cậy AI trung bình (%)
    avg_processing_time FLOAT DEFAULT 0.0,      -- Thời gian xử lý trung bình (giây)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. BẢNG ĐÁNH GIÁ ĐỘ ĐÚNG CỦA AI VÀ NGƯỜI DÙNG ĐÃ SỬA GÌ
CREATE TABLE IF NOT EXISTS ai_corrections (
    id SERIAL PRIMARY KEY,
    history_id INT NOT NULL REFERENCES scan_history(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    field_name VARCHAR(50) NOT NULL,           -- Tên trường bị sửa (id_number, full_name, nationality,...)
    ai_prediction TEXT,                        -- Kết quả AI nhận diện ban đầu
    user_corrected TEXT NOT NULL,              -- Kết quả thực tế người dùng sửa lại
    is_correct BOOLEAN DEFAULT FALSE,          -- Đánh giá: TRUE (AI đúng), FALSE (AI sai phải sửa)
    ai_confidence FLOAT,                       -- Độ tin cậy AI của trường này
    corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHỈ MỤC TỐI ƯU TÌM KIẾM
CREATE INDEX IF NOT EXISTS idx_history_user ON scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_results_id_number ON cccd_results(id_number);
CREATE INDEX IF NOT EXISTS idx_results_full_name ON cccd_results(full_name);
CREATE INDEX IF NOT EXISTS idx_corrections_history ON ai_corrections(history_id);
CREATE INDEX IF NOT EXISTS idx_stats_user ON scan_statistics(user_id);
