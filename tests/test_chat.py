# python -m unittest tests/test_chat.py
import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from ors.app.main import app
from ors.security.auth import get_current_client, Client

class TestChatRouter(unittest.TestCase):

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

    @patch("ors.app.routers.chat.invoke_llm")
    def test_chat_completions(self, mock_invoke_llm):
        mock_invoke_llm.return_value = "Mocked LLM Response"
        
        payload = {
            "free_models": True,
            "model_id": "meta-llama/llama-3.3-70b-instruct:free",
            "prompt_type": "basic",
            "user_prompt": "Hello!"
        }
        
        response = self.client.post("/chat/completions", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip('"'), "Mocked LLM Response")

    @patch("ors.app.routers.chat.invoke_llm")
    def test_chat_summarize(self, mock_invoke_llm):
        mock_invoke_llm.return_value = "Mocked Summary Output"
        
        payload = {
            "free_models": True,
            "model_id": "meta-llama/llama-3.3-70b-instruct:free",
            "text": "This is a long piece of text that needs to be summarized."
        }
        
        response = self.client.post("/chat/summarize", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"summary": "Mocked Summary Output"})

if __name__ == "__main__":
    unittest.main()
