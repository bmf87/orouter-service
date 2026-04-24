# python -m unittest tests/test_orouter_inv.py
import unittest
from unittest.mock import patch
from ors.llm.orouter_inv import is_free, get_free_models

class TestORouterInv(unittest.TestCase):

    def test_is_free_by_id(self):
        """Test that a model is marked free if ':free' is exclusively in the ID."""
        model = {"id": "meta-llama/llama-3-8b:free", "pricing": {"prompt": "0.1", "completion": "0.1"}}
        self.assertTrue(is_free(model))

    def test_is_free_by_pricing(self):
        """Test that a model is marked free if prompt and completion pricing are both mathematically 0."""
        model = {"id": "openai/some-model", "pricing": {"prompt": "0", "completion": 0.0}}
        self.assertTrue(is_free(model))

    def test_is_not_free(self):
        """Test that a model is realistically NOT marked free if pricing is > 0 and no ':free' in ID."""
        model = {"id": "openai/gpt-4o", "pricing": {"prompt": "0.01", "completion": "0.03"}}
        self.assertFalse(is_free(model))

    @patch('ors.llm.orouter_inv.get_models')
    def test_get_free_models(self, mock_get_models):
        """Test get_free_models filters gracefully and maps to identically grouped ModelInfo lists."""
        from ors.config.api_config import ModelInfo
        
        # Setup mock data mixed with free and paid permutations
        mock_get_models.return_value = [
            {"id": "meta-llama/llama-3:free", "pricing": {"prompt": "1", "completion": "1"}, "context_length": 8192},
            {"id": "openai/gpt-4o", "pricing": {"prompt": "0.01", "completion": "0.03"}},
            {"id": "google/gemma-7b", "pricing": {"prompt": "0", "completion": "0"}, "context_length": 4096},
            {"id": "anthropic/claude-3", "pricing": {"prompt": "3", "completion": "15"}} 
        ]
        
        expected_repo = {
            "meta-llama": [ModelInfo(id="meta-llama/llama-3:free", tier="free", context=8192)],
            "google": [ModelInfo(id="google/gemma-7b", tier="free", context=4096)]
        }
        
        # Execution flow
        result = get_free_models()
        
        # Validation checks
        self.assertEqual(result, expected_repo)
        mock_get_models.assert_called_once()


if __name__ == "__main__":
    unittest.main()
