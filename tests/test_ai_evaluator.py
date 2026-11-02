# tests/test_ai_evaluator.py
import unittest
import os
from unittest.mock import patch

from backend.core.ai_evaluator import (
    normalize_text,
    levenshtein_distance,
    calculate_field_accuracy,
    generate_character_diff,
    resolve_api_key,
    evaluate_ocr_accuracy,
    FIELD_WEIGHTS
)


class TestAIEvaluator(unittest.TestCase):

    def test_text_normalization(self):
        self.assertEqual(normalize_text("  NGUYỄN   VĂN   A  "), "NGUYỄN VĂN A")
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(normalize_text(12345), "12345")

    def test_levenshtein_distance(self):
        # Giống nhau hoàn toàn
        self.assertEqual(levenshtein_distance("001201012345", "001201012345"), 0)
        # Sai 1 ký tự
        self.assertEqual(levenshtein_distance("NGUYÊN", "NGUYỄN"), 1)
        # Trống
        self.assertEqual(levenshtein_distance("", "ABC"), 3)

    def test_field_accuracy(self):
        # 100% khi trùng hoàn toàn
        acc_full = calculate_field_accuracy("001201012345", "001201012345")
        self.assertEqual(acc_full, 100.0)

        # Sai 1 ký tự trong 10 ký tự -> 90%
        acc_part = calculate_field_accuracy("0123456789", "012345678X")
        self.assertEqual(acc_part, 90.0)

        # Trống cả 2 -> 100%
        self.assertEqual(calculate_field_accuracy("", ""), 100.0)

        # Một bên trống -> 0%
        self.assertEqual(calculate_field_accuracy("001201", ""), 0.0)

    def test_character_diff(self):
        diffs = generate_character_diff("NGUYÊN", "NGUYỄN")
        # Phải phát hiện phần giống "NGUY", thay thế "Ê" -> "Ễ", và giống "N"
        self.assertTrue(len(diffs) >= 2)
        has_replace = any(d["type"] == "replace" for d in diffs)
        self.assertTrue(has_replace)

    def test_key_resolution_priority(self):
        # Kịch bản 1: Người dùng tự nhập key -> Phải ưu tiên dùng key người dùng
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSy_ENV_SYSTEM_DEFAULT_KEY_12345"}):
            key, source = resolve_api_key(user_key="AIzaSy_USER_CUSTOM_KEY_67890", provider="gemini")
            self.assertEqual(key, "AIzaSy_USER_CUSTOM_KEY_67890")
            self.assertEqual(source, "user")

        # Kịch bản 2: Người dùng để trống -> Phải tự động fallback về key .env hệ thống
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSy_ENV_SYSTEM_DEFAULT_KEY_12345"}):
            key, source = resolve_api_key(user_key="", provider="gemini")
            self.assertEqual(key, "AIzaSy_ENV_SYSTEM_DEFAULT_KEY_12345")
            self.assertEqual(source, "env")

        # Kịch bản 3: Không có cả 2 -> Trả về None và source "none"
        with patch.dict(os.environ, {}, clear=True):
            key, source = resolve_api_key(user_key=None, provider="gemini")
            self.assertIsNone(key)
            self.assertEqual(source, "none")

    def test_evaluate_ocr_accuracy_full_match(self):
        sample_card = {
            "so_cccd": "001201012345",
            "ho_ten": "NGUYỄN VĂN A",
            "ngay_sinh": "01/01/2001",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Hà Nội",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "01/01/2041"
        }
        res = evaluate_ocr_accuracy(local_result=sample_card, oracle_result=sample_card, provider="gemini", key_source="env")
        self.assertEqual(res["overall_accuracy"], 100.0)
        self.assertEqual(res["matched_fields"], 8)
        self.assertEqual(res["status"], "success")

    def test_evaluate_ocr_accuracy_with_errors(self):
        local_card = {
            "so_cccd": "001201012345",
            "ho_ten": "NGUYÊN VĂN A", # Sai 1 dấu
            "ngay_sinh": "01/01/2001",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Hà Nội",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "01/01/2041"
        }
        oracle_card = {
            "so_cccd": "001201012345",
            "ho_ten": "NGUYỄN VĂN A",
            "ngay_sinh": "01/01/2001",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Hà Nội",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "01/01/2041"
        }
        res = evaluate_ocr_accuracy(local_result=local_card, oracle_result=oracle_card, provider="gemini", key_source="user")
        self.assertTrue(95.0 <= res["overall_accuracy"] < 100.0)
        self.assertEqual(res["matched_fields"], 7)
        self.assertEqual(res["key_source"], "user")


if __name__ == "__main__":
    unittest.main()
