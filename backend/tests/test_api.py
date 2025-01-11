import unittest
from fastapi.testclient import TestClient
from app.main import app
from trading.config import BotConfig, TradingConfig, ConfigUpdate

class TestAPI(unittest.TestCase):
    """API 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.client = TestClient(app)

    def test_health_check(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_get_config(self):
        """설정 조회 엔드포인트 테스트"""
        response = self.client.get("/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("bot_config", data)
        self.assertIn("trading_config", data)

    def test_update_config(self):
        """설정 업데이트 엔드포인트 테스트"""
        bot_config = BotConfig(
            symbol="005930",
            total_divisions=10,
            log_dir="logs",
            app_key="test",
            app_secret="test",
            account_number="test",
            account_code="test"
        )
        trading_config = TradingConfig(
            stock_code="005930",
            target_price=70000,
            quantity=10,
            first_buy_amount=1000000,
            pre_turn_threshold=20,
            quarter_loss_start=39,
            trading_interval=1,
            max_trades_per_day=10,
            use_real_trading=False
        )
        config = ConfigUpdate(bot_config=bot_config, trading_config=trading_config)
        response = self.client.post("/config", json=config.model_dump())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_reset_bot(self):
        """봇 초기화 엔드포인트 테스트"""
        response = self.client.post("/config/reset")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_bot_control(self):
        """봇 제어 엔드포인트 테스트"""
        # 설정 업데이트
        bot_config = BotConfig(
            symbol="005930",
            total_divisions=10,
            log_dir="logs",
            app_key="test",
            app_secret="test",
            account_number="test",
            account_code="test"
        )
        trading_config = TradingConfig(
            stock_code="005930",
            target_price=70000,
            quantity=10,
            first_buy_amount=1000000,
            pre_turn_threshold=20,
            quarter_loss_start=39,
            trading_interval=1,
            max_trades_per_day=10,
            use_real_trading=False
        )
        config = ConfigUpdate(bot_config=bot_config, trading_config=trading_config)
        self.client.post("/config", json=config.model_dump())

        # 봇 시작
        response = self.client.post("/config/start")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # 봇 상태 확인
        response = self.client.get("/config/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_running"])

        # 봇 중지
        response = self.client.post("/config/stop")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

if __name__ == '__main__':
    unittest.main()
