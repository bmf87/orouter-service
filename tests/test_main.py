# python -m unittest tests/test_main.py
import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from ors.app.main import app
from ors.security.auth import get_current_client, Client

class TestMainApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Temporarily patch the environment so Langchain initialization doesn't fail on missing API keys
        cls.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key_for_test"})
        cls.env_patcher.start()
        
        # Override the bearer token dependency to bypass manual auth checks across HTTP fetches purely for endpoint testing
        app.dependency_overrides[get_current_client] = lambda: Client(client_id="test-client-bypasser")
        
        # raise_server_exceptions=False so we can test HTTP errors gracefully
        with TestClient(app, raise_server_exceptions=False) as client:
            cls.client = client

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.env_patcher.stop()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        
    def test_info_endpoint(self):
        response = self.client.get("/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("name"), "orouter-service")
        self.assertIn("version", data)
        self.assertIn("routes", data)

if __name__ == "__main__":
    unittest.main()
