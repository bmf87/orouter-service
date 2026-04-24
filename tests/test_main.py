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

    def test_get_models_free(self):
        response = self.client.get("/models?free_models=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", data)

    def test_get_models_paid(self):
        response = self.client.get("/models?free_models=false")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        # Using deepseek since it's the model you have listed in paid_models.yaml
        self.assertIn("deepseek/deepseek-r1-0528", data)

    def test_get_models_by_provider_free(self):
        # Queries meta-llama since the OpenRouter API parsing structure natively groups based on strict id prefix splitting
        response = self.client.get("/models/meta-llama?free_models=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", data)

    def test_get_models_by_provider_paid(self):
        response = self.client.get("/models/openai?free_models=false")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        # Verifies it retrieves the paid models and filters out the free ones
        self.assertIn("openai/gpt-5.4-nano", data)
        self.assertNotIn("openai/gpt-oss-120b:free", data)
        
    def test_get_models_by_provider_invalid(self):
        response = self.client.get("/models/invalid_provider?free_models=true")
        # FastAPI now explicitly throws customized 404 missing repository errors rather than generic 500 exceptions
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
