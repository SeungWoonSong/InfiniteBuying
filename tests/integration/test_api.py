"""API 엔드포인트 테스트"""
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
                "total_divisions": 10,
                "log_dir": "logs",
                "app_key": "test",
                "app_secret": "test",
                "account_number": "test",
                "account_code": "test"
            },
            "trading_config": {
                "initial_amount": 1000000,
                "single_amount": 200000,
                "min_order_amount": 100000,
                "loss_cut_rate": 0.03,
                "profit_rate": 0.02,
                "max_buy_times": 5,
                "trading_interval": 1.0
            }
        }

    def test_health_check(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_update_config(self):
        """설정 업데이트 엔드포인트 테스트"""
        response = self.client.post("/api/v1/config", json=self.test_config)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

    def test_get_config(self):
        """설정 조회 엔드포인트 테스트"""
        # 먼저 설정을 업데이트
        self.client.post("/api/v1/config", json=self.test_config)

        # 설정 조회
        response = self.client.get("/api/v1/config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["bot_config"]["symbol"], "005930")

    def test_bot_control(self):
        """봇 제어 엔드포인트 테스트"""
        # 먼저 설정을 업데이트
        response = self.client.post("/api/v1/config", json=self.test_config)
        self.assertEqual(response.status_code, 200)

        # 봇 시작
        response = self.client.post("/api/v1/bot/start")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        # 봇 상태 확인
        response = self.client.get("/api/v1/bot/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["is_running"], True)

        # 봇 중지
        response = self.client.post("/api/v1/bot/stop")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

    def test_reset_bot(self):
        """봇 초기화 엔드포인트 테스트"""
        # 먼저 설정을 업데이트
        response = self.client.post("/api/v1/config", json=self.test_config)
        self.assertEqual(response.status_code, 200)

        # 봇 초기화
        response = self.client.post("/api/v1/bot/reset")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

if __name__ == '__main__':
    unittest.main()
