# python -m unittest tests/test_model.py
import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from ors.app.main import app
from ors.security.auth import get_current_client, Client

class TestModelRouter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key_for_test"})
        cls.env_patcher.start()
        
        app.dependency_overrides[get_current_client] = lambda: Client(client_id="test-client-bypasser")
        
        with TestClient(app, raise_server_exceptions=False) as client:
            cls.client = client

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.env_patcher.stop()

    def test_get_models_free(self):
        response = self.client.get("/model/models?free_models=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", data)

    def test_get_models_paid(self):
        response = self.client.get("/model/models?free_models=false")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("deepseek/deepseek-r1-0528", data)

    def test_get_models_by_provider_free(self):
        response = self.client.get("/model/meta-llama/models?free_models=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", data)

    def test_get_models_by_provider_paid(self):
        response = self.client.get("/model/openai/models?free_models=false")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("openai/gpt-5.4-nano", data)
        self.assertNotIn("openai/gpt-oss-120b:free", data)
        
    def test_get_models_by_provider_invalid(self):
        response = self.client.get("/model/invalid_provider/models?free_models=true")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
