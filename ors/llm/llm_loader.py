import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from ors.config.api_config import free_model_repo, paid_model_repo, ModelInfo
from ors import constants


class LLMFactory:
    
    def __init__(self, temperature: float = 0.7, dynamic_free_model_repo: Dict[str, List[ModelInfo]] = None):
        # Use getattr to safely retrieve api_key if dynamically set, or fallback to environment variables
        self.api_key = getattr(constants, 'openrouter_api_key', os.getenv("OPENROUTER_API_KEY"))
        self.api_base_url = getattr(constants, 'api_base_url', "https://openrouter.ai/api/v1")
        self.temperature = temperature
        self.default_headers = {
            "X-Title": getattr(constants, 'app_name', 'orouter-service'),
            "HTTP-Referer": getattr(constants, 'app_dns', 'orouter-service')
        }
        self.free_model_repo = free_model_repo if not dynamic_free_model_repo else dynamic_free_model_repo
        self.paid_model_repo = paid_model_repo
    
    def get_llm(self,model_id: str, free_models: bool = True, temperature: float = 0.7) -> ChatOpenAI:
        """
        Factory method to get a ChatOpenAI instance for a given model.
        
        Args:
            model_id (str): The ID of the model to load (e.g. 'meta-llama/llama-3.2-11b-vision-instruct')
            free_models (bool): Whether to look in the free model repository or paid repository.
            temperature (float): The temperature for the LLM.
            
        Returns:
            ChatOpenAI: The instantiated LLM.
        """
        valid_model_id = self.get_model_by_id(model_id, free_models)
        return self._get_llm(valid_model_id)
        
    def _get_llm(self, model_id: str) -> ChatOpenAI:
        llm = ChatOpenAI(
            model_name=model_id,
            openai_api_key=self.api_key,
            openai_api_base=self.api_base_url,
            temperature=self.temperature,
            default_headers=self.default_headers
        )
        return llm

    def get_model_by_id(self, model_id: str, free_models: bool = True) -> str:
        """
        Validates if the provided model_id exists in the specified repository.
        """
        repo = self.free_model_repo if free_models else self.paid_model_repo
        models = self.get_models(repo)
        
        if models and model_id not in models:
            repo_type = "free" if free_models else "paid"
            raise ValueError(f"Model '{model_id}' not found in {repo_type} model repository.")
            
        return model_id

    def get_models(self, model_repo: dict) -> list:
        """
        Flatten a model repository dictionary into a simple list of models.
        """
        models = []
        for provider_models in model_repo.values():
            for m in provider_models:
                models.append(m.id if hasattr(m, 'id') else m)
        return models

    def get_model_by_provider(self, provider: str, free_models: bool = True) -> list:
        """
        Get the model IDs for a specific provider.

        Args:
            provider (str): The name of the provider (e.g., 'llama', 'google').
            free_models (bool): Look up in the free vs paid models repository

        Returns:
            list: A list of model IDs for the specified provider.
        """
        repo = self.free_model_repo if free_models else self.paid_model_repo
        if provider in repo:
            return [m.id if hasattr(m, 'id') else m for m in repo[provider]]
        else:
            repo_type = "free" if free_models else "paid"
            raise ValueError(f"Provider '{provider}' not found in {repo_type} model repository.")

    def get_providers(self, free_models: bool = True) -> list:
        """
        Get all available model providers from a repository.
        """
        repo = self.free_model_repo if free_models else self.paid_model_repo
        return list(repo.keys())
        