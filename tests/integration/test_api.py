"""API 통합 테스트"""
import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestAPI(unittest.TestCase):
    """API 엔드포인트 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.client = TestClient(app)
        self.test_config = {
            "bot_config": {
                "symbol": "005930",
                "total_divisions": 5,
                "log_dir": "logs",
                "app_key": "test_app_key",
                "app_secret": "test_app_secret",
                "account_number": "test_account",
                "account_code": "01"
            },
            "trading_config": {
                "stock_code": "005930",
                "target_price": 50000,
                "quantity": 10,
                "first_buy_amount": 1000000,
                "pre_turn_threshold": 5.0,
                "quarter_loss_start": 10.0,
                "trading_interval": 60,
                "max_trades_per_day": 20,
                "use_real_trading": False
            }
        }

    def test_health_check(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_get_config(self):
        """설정 조회 엔드포인트 테스트"""
        response = self.client.get("/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn("bot_config", response.json())
        self.assertIn("trading_config", response.json())

    def test_update_config(self):
        """설정 업데이트 엔드포인트 테스트"""
        response = self.client.post("/config", json=self.test_config)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

    def test_bot_control(self):
        """봇 제어 엔드포인트 테스트"""
        # 먼저 설정을 업데이트
        self.client.post("/config", json=self.test_config)
        
        # 봇 시작
        response = self.client.post("/config/start")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        # 봇 상태 확인
        response = self.client.get("/config/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["is_running"], True)

        # 봇 중지
        response = self.client.post("/config/stop")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

    def test_reset_bot(self):
        """봇 초기화 엔드포인트 테스트"""
        response = self.client.post("/config/reset")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
