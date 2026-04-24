# python -m unittest tests/test_llm_loader.py
import unittest
import os
from unittest.mock import patch
from ors.llm.llm_loader import LLMFactory
from langchain_openai import ChatOpenAI

class TestLLMFactory(unittest.TestCase):

    def setUp(self):
        # We can temporarily patch the environment so Langchain initialization doesn't fail on missing API keys
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key_for_test"})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_get_llm_free_model(self):
        model_id = "meta-llama/llama-3.3-70b-instruct:free"
        factory = LLMFactory()
        llm = factory.get_llm(model_id=model_id, free_models=True)
        
        self.assertIsInstance(llm, ChatOpenAI)
        self.assertEqual(llm.model_name, model_id)
        self.assertEqual(llm.temperature, 0.7)  # default temperature

    def test_get_llm_paid_model(self):
        model_id = "openai/gpt-5.4-nano"
        factory = LLMFactory(temperature=0.5)  # Set temperature to 0.5 for this test
        llm = factory.get_llm(model_id=model_id, free_models=False)
        
        self.assertIsInstance(llm, ChatOpenAI)
        self.assertEqual(llm.model_name, model_id)
        self.assertEqual(llm.temperature, 0.5)

    def test_get_llm_invalid_free_model(self):
        model_id = "invalid-model-name"
        factory = LLMFactory()
        with self.assertRaises(ValueError) as context:
            factory.get_llm(model_id=model_id, free_models=True)
            
        self.assertIn("not found in free model repository", str(context.exception))

    def test_get_llm_invalid_paid_model(self):
        model_id = "invalid-model-name"
        factory = LLMFactory()
        with self.assertRaises(ValueError) as context:
            factory.get_llm(model_id=model_id, free_models=False)
            
        self.assertIn("not found in paid model repository", str(context.exception))

    def test_get_model_by_provider(self):
        factory = LLMFactory()
        
        # Test valid free provider
        models = factory.get_model_by_provider("llama", free_models=True)
        self.assertIsInstance(models, list)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", models)
        
        # Test invalid provider
        with self.assertRaises(ValueError):
            factory.get_model_by_provider("invalid_provider", free_models=True)

    def test_get_models_list(self):
        factory = LLMFactory()
        models = factory.get_models(factory.free_model_repo)
        
        self.assertIsInstance(models, list)
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", models)
        self.assertIn("openai/gpt-oss-120b:free", models)

if __name__ == "__main__":
    unittest.main()
