# tests/test_ai_evaluation_flow.py
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestAIEvaluationFlow(unittest.TestCase):

    def test_evaluate_status(self):
        res = client.get("/predict/evaluate-status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("system_gemini_configured", data)
        self.assertIn("system_openai_configured", data)
        self.assertIn("system_key_configured", data)

    def test_test_key_endpoint_empty(self):
        with patch("backend.api.routes_ocr.resolve_api_key", return_value=(None, "none")):
            res = client.post("/predict/evaluate-test-key", data={"provider": "gemini"})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertFalse(data["valid"])

    def test_evaluate_on_demand_with_mock(self):
        mock_oracle = {
            "so_cccd": "001204014664",
            "ho_ten": "NGUYỄN MINH QUÂN",
            "ngay_sinh": "09/09/2004",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Bắc Ninh",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "09/09/2044"
        }

        local_data = {
            "so_cccd": "001204014664",
            "ho_ten": "NGUYÊN MINH QUÂN", # sai 1 dấu
            "ngay_sinh": "09/09/2004",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Bắc Ninh",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "09/09/2044"
        }

        with patch("backend.core.ai_evaluator.extract_card_oracle_gemini", return_value=mock_oracle):
            with open("data/input/cccd1.jpg", "rb") as f:
                res = client.post(
                    "/predict/evaluate-on-demand",
                    files={"file": ("cccd1.jpg", f, "image/jpeg")},
                    data={"local_data_json": '{"so_cccd": "001204014664", "ho_ten": "NGUYÊN MINH QUÂN", "ngay_sinh": "09/09/2004", "gioi_tinh": "Nam", "quoc_tich": "Việt Nam", "que_quan": "Bắc Ninh", "noi_ctru": "Ba Đình, Hà Nội", "ngay_het_han": "09/09/2044"}'},
                    headers={"X-AI-API-Key": "AIzaSy_mock_test_key_for_unit_test", "X-AI-Provider": "gemini"}
                )

            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertTrue(data["overall_accuracy"] >= 95.0)
            self.assertEqual(data["matched_fields"], 7)
            self.assertEqual(data["total_fields"], 8)
            self.assertEqual(data["key_source"], "user")

    def test_predict_image_with_evaluation_flag(self):
        mock_oracle = {
            "so_cccd": "001204014664",
            "ho_ten": "NGUYỄN MINH QUÂN",
            "ngay_sinh": "09/09/2004",
            "gioi_tinh": "Nam",
            "quoc_tich": "Việt Nam",
            "que_quan": "Bắc Ninh",
            "noi_ctru": "Ba Đình, Hà Nội",
            "ngay_het_han": "09/09/2044"
        }

        with patch("backend.core.ai_evaluator.extract_card_oracle_gemini", return_value=mock_oracle):
            with open("data/input/cccd1.jpg", "rb") as f:
                res = client.post(
                    "/predict/image",
                    files={"file": ("cccd1.jpg", f, "image/jpeg")},
                    data={"input_source": "IMAGE", "evaluate_with_ai": "true"},
                    headers={"X-AI-API-Key": "AIzaSy_mock_key_1234567890", "X-AI-Provider": "gemini"}
                )

            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("ai_evaluation", data)
            eval_data = data["ai_evaluation"]
            self.assertIsNotNone(eval_data)
            self.assertEqual(eval_data["status"], "success")
            self.assertTrue(eval_data["overall_accuracy"] > 70.0)


if __name__ == "__main__":
    unittest.main()
