# backend/core/ai_evaluator.py
"""
Module đánh giá độ chính xác OCR CCCD tự động bằng External Vision AI (AI Oracle).
Hỗ trợ kiến trúc Hybrid API Key:
- Tầng 1: Key mặc định từ biến môi trường / file .env của máy chủ
- Tầng 2: Key cá nhân do người dùng tự nhập từ giao diện Web UI (ưu tiên cao nhất)
"""

import os
import re
import json
import base64
import logging
import unicodedata
import difflib
from typing import Optional, Dict, Any, Tuple, List
import requests
from dotenv import load_dotenv

# Tải cấu hình biến môi trường từ .env
load_dotenv()

logger = logging.getLogger(__name__)

# Bảng trọng số 8 trường thông tin CCCD
FIELD_WEIGHTS = {
    "so_cccd": 0.25,        # 1. Số CCCD (quan trọng nhất)
    "ho_ten": 0.20,         # 2. Họ và tên
    "noi_ctru": 0.15,       # 3. Nơi thường trú
    "que_quan": 0.15,       # 4. Quê quán
    "ngay_sinh": 0.10,      # 5. Ngày sinh
    "ngay_het_han": 0.05,   # 6. Có giá trị đến
    "gioi_tinh": 0.05,      # 7. Giới tính
    "quoc_tich": 0.05       # 8. Quốc tịch
}

FIELD_LABELS = {
    "so_cccd": "Số CCCD",
    "ho_ten": "Họ và tên",
    "ngay_sinh": "Ngày sinh",
    "gioi_tinh": "Giới tính",
    "quoc_tich": "Quốc tịch",
    "que_quan": "Quê quán",
    "noi_ctru": "Nơi thường trú",
    "ngay_het_han": "Có giá trị đến"
}

# Mapping các key tương đương giữa các schema
FIELD_KEY_ALIASES = {
    "id_number": "so_cccd",
    "id": "so_cccd",
    "full_name": "ho_ten",
    "name": "ho_ten",
    "dob": "ngay_sinh",
    "date_of_birth": "ngay_sinh",
    "gender": "gioi_tinh",
    "sex": "gioi_tinh",
    "nationality": "quoc_tich",
    "origin_location": "que_quan",
    "origin_place": "que_quan",
    "home_town": "que_quan",
    "residence": "noi_ctru",
    "current_place": "noi_ctru",
    "address": "noi_ctru",
    "expiry_date": "ngay_het_han",
    "expire_date": "ngay_het_han",
    "valid_until": "ngay_het_han"
}


def normalize_text(text: Any) -> str:
    """Chuẩn hóa văn bản tiếng Việt Unicode NFC, xóa khoảng trắng thừa."""
    if text is None:
        return ""
    text_str = str(text).strip()
    # Chuẩn hóa về Unicode Form NFC
    text_str = unicodedata.normalize("NFC", text_str)
    # Rút gọn khoảng trắng liên tiếp
    text_str = re.sub(r"\s+", " ", text_str)
    return text_str


def levenshtein_distance(s1: str, s2: str) -> int:
    """Tính khoảng cách Levenshtein (số thao tác chèn, xóa, thay thế ký tự tối thiểu)."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_field_accuracy(local_val: str, oracle_val: str) -> float:
    """
    Tính % độ chính xác giữa kết quả local và oracle (0.0 đến 100.0).
    Sử dụng công thức Levenshtein Ratio chuẩn hóa.
    """
    s1 = normalize_text(local_val)
    s2 = normalize_text(oracle_val)

    if not s1 and not s2:
        return 100.0
    if not s1 or not s2:
        return 0.0

    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 100.0

    dist = levenshtein_distance(s1, s2)
    acc = max(0.0, 1.0 - (dist / max_len)) * 100.0
    return round(acc, 1)


def generate_character_diff(local_val: str, oracle_val: str) -> List[Dict[str, str]]:
    """
    Tạo bản đồ diff ký tự chi tiết giữa chuỗi local (VietOCR) và oracle (AI chuẩn).
    Trả về danh sách các token với type: 'equal', 'delete' (thừa), 'insert' (thiếu/cần sửa).
    """
    s1 = normalize_text(local_val)
    s2 = normalize_text(oracle_val)

    matcher = difflib.SequenceMatcher(None, s1, s2)
    diffs = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            diffs.append({"type": "equal", "text": s1[i1:i2]})
        elif tag == "replace":
            diffs.append({
                "type": "replace",
                "local": s1[i1:i2],
                "oracle": s2[j1:j2]
            })
        elif tag == "delete":
            diffs.append({"type": "delete", "text": s1[i1:i2]})
        elif tag == "insert":
            diffs.append({"type": "insert", "text": s2[j1:j2]})

    return diffs


try:
    _LAST_ENV_MTIME = os.path.getmtime(".env") if os.path.exists(".env") else 0.0
except Exception:
    _LAST_ENV_MTIME = 0.0

GEMINI_MODELS_ORDER = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]


def _check_and_reload_env():
    """Tự động nạp lại file .env khi file bị thay đổi trên đĩa."""
    global _LAST_ENV_MTIME
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            mtime = os.path.getmtime(env_file)
            if mtime > _LAST_ENV_MTIME:
                load_dotenv(override=True)
                _LAST_ENV_MTIME = mtime
        except Exception:
            pass


def resolve_api_key(
    user_key: Optional[str] = None,
    provider: str = "gemini"
) -> Tuple[Optional[str], str]:
    """
    Bộ phân giải API Key phân cấp (Hierarchical Key Resolver):
    Ưu tiên 1: user_key từ giao diện người dùng
    Ưu tiên 2: key mặc định từ file .env / biến môi trường
    Trả về: (api_key_str, source_str) với source là 'user', 'env', hoặc 'none'
    """
    provider_clean = (provider or "gemini").lower().strip()

    # 1. Kiểm tra key cá nhân của người dùng
    if user_key and isinstance(user_key, str) and user_key.strip():
        clean_user_key = user_key.strip().strip('"').strip("'")
        if len(clean_user_key) >= 15:
            return clean_user_key, "user"

    # 2. Tự động kiểm tra và nạp lại file .env nếu có thay đổi
    _check_and_reload_env()

    env_var_name = "GEMINI_API_KEY" if provider_clean == "gemini" else "OPENAI_API_KEY"
    env_key = os.getenv(env_var_name, "").strip().strip('"').strip("'")
    if env_key:
        return env_key, "env"

    return None, "none"


def is_system_key_configured(provider: str = "gemini") -> bool:
    """Kiểm tra máy chủ đã được cấu hình API Key mặc định trong .env hay chưa."""
    key, _ = resolve_api_key(user_key=None, provider=provider)
    return key is not None and len(key) > 10


def test_api_key(api_key: str, provider: str = "gemini") -> Dict[str, Any]:
    """Kiểm tra tính hợp lệ và kết nối của API Key với xử lý lỗi thân thiện cho Google AI Studio Free Tier."""
    clean_key = (api_key or "").strip().strip('"').strip("'")
    if not clean_key:
        return {"valid": False, "message": "API Key không được để trống"}

    provider_clean = (provider or "gemini").lower().strip()

    if provider_clean == "gemini":
        last_error_detail = ""

        for model in GEMINI_MODELS_ORDER:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={clean_key}"
                payload = {
                    "contents": [{"parts": [{"text": "Reply JSON: {\"status\": \"ok\"}"}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    return {
                        "valid": True,
                        "provider": "gemini",
                        "model": model,
                        "message": f"Kết nối Google Gemini API ({model}) thành công! Key hoạt động tốt."
                    }
                else:
                    err_json = {}
                    try:
                        err_json = res.json().get("error", {})
                    except Exception:
                        pass

                    msg = err_json.get("message", res.text)
                    status_str = err_json.get("status", "")
                    # Nếu 404, 503, 429: ghi nhận và tiếp tục thử model khác trong danh sách
                    if res.status_code in (404, 503, 429):
                        last_error_detail = f"[{model} - {res.status_code}] {msg}"
                        continue

                    # Nếu lỗi là API key không hợp lệ hoặc location/permission
                    user_msg = msg
                    if "API key not valid" in msg or status_str == "INVALID_ARGUMENT":
                        user_msg = "API Key không hợp lệ. Vui lòng kiểm tra lại key từ Google AI Studio (bắt đầu bằng AIzaSy... hoặc AQ...)."
                    elif "User location is not supported" in msg:
                        user_msg = "Google AI Studio báo: Vị trí mạng / VPN hiện tại không được hỗ trợ Free Tier. Hãy tắt VPN hoặc đổi sang mạng IP Việt Nam thông thường."
                    elif "has not been used in project" in msg or "disabled" in msg:
                        user_msg = "Dự án Google Cloud chưa kích hoạt 'Generative Language API'. Hãy kiểm tra cài đặt API trong Google Cloud Console."

                    return {
                        "valid": False,
                        "provider": "gemini",
                        "model": model,
                        "message": f"Gemini API lỗi ({res.status_code}): {user_msg}"
                    }
            except Exception as e:
                last_error_detail = f"[{model}] {str(e)}"
                continue

        # Phân tích lỗi cuối cùng nếu tất cả model đều thử thất bại
        user_friendly_detail = last_error_detail
        if "API key not valid" in last_error_detail:
            user_friendly_detail = "API Key không hợp lệ. Vui lòng kiểm tra lại key từ Google AI Studio."
        elif "Resource has been exhausted" in last_error_detail or "429" in last_error_detail:
            user_friendly_detail = "Tất cả model Gemini đều đang vượt hạn mức Free Tier (Rate Limit). Vui lòng đợi 1-2 phút rồi thử lại."
        elif "503" in last_error_detail or "experiencing high demand" in last_error_detail:
            user_friendly_detail = "Hệ thống máy chủ Google Gemini hiện đang quá tải (High demand / 503). Vui lòng thử lại sau giây lát."

        return {
            "valid": False,
            "provider": "gemini",
            "message": f"Không thể kết nối Gemini API: {user_friendly_detail}"
        }

    elif provider_clean == "openai":
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                return {
                    "valid": True,
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "message": "Kết nối OpenAI API thành công! Key hợp lệ."
                }
            else:
                err_data = res.json().get("error", {})
                msg = err_data.get("message", f"HTTP {res.status_code}")
                return {"valid": False, "provider": "openai", "message": f"OpenAI API báo lỗi: {msg}"}
        except Exception as e:
            return {"valid": False, "provider": "openai", "message": f"Không thể kết nối OpenAI API: {str(e)}"}

    return {"valid": False, "message": f"Provider không hỗ trợ: {provider}"}


def extract_card_oracle_gemini(image_bytes: bytes, api_key: str) -> Dict[str, Any]:
    """Sử dụng Gemini Vision làm Ground Truth Oracle với fallback đa tầng linh hoạt."""
    clean_key = (api_key or "").strip().strip('"').strip("'")
    b64_img = base64.b64encode(image_bytes).decode("utf-8")

    prompt_text = (
        "Bạn là chuyên gia thẩm định văn bản hành chính Việt Nam. "
        "Hãy đọc thật chính xác thông tin trên mặt trước thẻ Căn cước công dân (CCCD) trong ảnh. "
        "Trả về định dạng JSON thuần túy có đầy đủ 8 trường sau (giữ nguyên dấu tiếng Việt và chữ hoa):\n"
        "{\n"
        '  "so_cccd": "12 chữ số CCCD (chỉ số)",\n'
        '  "ho_ten": "Họ và tên viết hoa có dấu",\n'
        '  "ngay_sinh": "Ngày sinh dạng dd/mm/yyyy",\n'
        '  "gioi_tinh": "Nam hoặc Nữ",\n'
        '  "quoc_tich": "Việt Nam",\n'
        '  "que_quan": "Quê quán đầy đủ có dấu",\n'
        '  "noi_ctru": "Nơi thường trú đầy đủ có dấu",\n'
        '  "ngay_het_han": "Có giá trị đến dạng dd/mm/yyyy (hoặc Không thời hạn)"\n'
        "}\n"
        "Chỉ trả về JSON, không kèm bất kỳ giải thích nào khác."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64_img
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    last_err = ""
    for model in GEMINI_MODELS_ORDER:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={clean_key}"
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                res_json = res.json()
                candidates = res_json.get("candidates", [])
                if not candidates:
                    continue

                text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text_content = text_content.strip()
                # Loại bỏ code blocks markdown nếu có
                if text_content.startswith("```"):
                    text_content = re.sub(r"^```(?:json)?\s*", "", text_content)
                    text_content = re.sub(r"\s*```$", "", text_content)

                return json.loads(text_content)
            else:
                err = res.json().get("error", {}).get("message", res.text)
                last_err = f"({res.status_code}): {err}"
                if res.status_code in (404, 503, 429):
                    continue
                raise ValueError(f"Gemini API lỗi {last_err}")
        except ValueError:
            raise
        except Exception as net_err:
            last_err = str(net_err)
            continue

    raise ValueError(f"Gemini API không thể hoàn thành trên các model ({', '.join(GEMINI_MODELS_ORDER)}): {last_err}")


def extract_card_oracle_openai(image_bytes: bytes, api_key: str) -> Dict[str, Any]:
    """Sử dụng OpenAI gpt-4o-mini Vision làm Ground Truth Oracle."""
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt_text = (
        "Trích xuất thông tin mặt trước thẻ CCCD Việt Nam trong ảnh thành JSON chứa 8 trường:\n"
        "so_cccd, ho_ten, ngay_sinh, gioi_tinh, quoc_tich, que_quan, noi_ctru, ngay_het_han."
    )

    payload = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ],
        "temperature": 0.1
    }

    res = requests.post(url, headers=headers, json=payload, timeout=25)
    if res.status_code != 200:
        err = res.json().get("error", {}).get("message", res.text)
        raise ValueError(f"OpenAI API lỗi ({res.status_code}): {err}")

    content = res.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def evaluate_ocr_accuracy(
    local_result: Dict[str, Any],
    oracle_result: Dict[str, Any],
    provider: str = "gemini",
    key_source: str = "env"
) -> Dict[str, Any]:
    """
    So sánh đối soát kết quả trích xuất của pipeline nội bộ và Oracle Vision AI.
    Tính % chính xác từng trường và % tổng thể có trọng số.
    """
    # Chuẩn hóa key của local_result và oracle_result
    def map_to_standard(raw_dict: Dict[str, Any]) -> Dict[str, str]:
        std = {}
        for k, v in raw_dict.items():
            k_clean = str(k).lower().strip()
            std_k = FIELD_KEY_ALIASES.get(k_clean, k_clean)
            if std_k in FIELD_WEIGHTS:
                std[std_k] = normalize_text(v)
        return std

    local_std = map_to_standard(local_result)
    oracle_std = map_to_standard(oracle_result)

    field_evaluations = []
    weighted_acc_sum = 0.0
    total_weights = 0.0
    matched_fields = 0

    for field_key, weight in FIELD_WEIGHTS.items():
        loc_val = local_std.get(field_key, "")
        ora_val = oracle_std.get(field_key, "")

        acc = calculate_field_accuracy(loc_val, ora_val)
        is_perfect = (acc >= 99.0)
        if is_perfect:
            matched_fields += 1

        weighted_acc_sum += (acc * weight)
        total_weights += weight

        diffs = generate_character_diff(loc_val, ora_val)

        field_evaluations.append({
            "field_name": field_key,
            "field_label": FIELD_LABELS.get(field_key, field_key),
            "weight": weight,
            "local_value": loc_val,
            "oracle_value": ora_val,
            "accuracy_percent": acc,
            "is_match": is_perfect,
            "diffs": diffs
        })

    overall_accuracy = round(weighted_acc_sum / max(1e-5, total_weights), 1)

    return {
        "overall_accuracy": overall_accuracy,
        "matched_fields": matched_fields,
        "total_fields": len(FIELD_WEIGHTS),
        "field_accuracies": field_evaluations,
        "provider": provider,
        "key_source": key_source,
        "status": "success",
        "oracle_raw": oracle_std
    }


def evaluate_pipeline_with_ai(
    image_bytes: bytes,
    local_result: Dict[str, Any],
    user_key: Optional[str] = None,
    provider: str = "gemini"
) -> Dict[str, Any]:
    """
    Hàm giao tiếp cấp cao:
    1. Phân giải API Key (User key ưu tiên hơn .env)
    2. Gọi Oracle Vision AI tương ứng
    3. Đối soát & tính % độ chính xác
    An toàn: Bắt mọi lỗi mạng / quota để không bao giờ làm hỏng quy trình OCR chính.
    """
    key, source = resolve_api_key(user_key=user_key, provider=provider)
    if not key:
        return {
            "status": "error",
            "message": "Chưa có API Key! Vui lòng cấu hình GEMINI_API_KEY trong file .env hoặc nhập Key cá nhân trên giao diện.",
            "overall_accuracy": None,
            "key_source": "none"
        }

    provider_clean = (provider or "gemini").lower().strip()

    try:
        if provider_clean == "openai":
            oracle_data = extract_card_oracle_openai(image_bytes, key)
        else:
            oracle_data = extract_card_oracle_gemini(image_bytes, key)

        eval_res = evaluate_ocr_accuracy(
            local_result=local_result,
            oracle_result=oracle_data,
            provider=provider_clean,
            key_source=source
        )
        return eval_res

    except Exception as e:
        logger.warning(f"Lỗi khi thẩm định AI Oracle: {e}")
        return {
            "status": "error",
            "message": f"Không thể thẩm định với {provider}: {str(e)}",
            "overall_accuracy": None,
            "provider": provider_clean,
            "key_source": source
        }
