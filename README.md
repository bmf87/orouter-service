# ORouter Service

ORouter Service is a secure, authenticated FastAPI gateway designed to act as a robust Large Language Model (LLM) multiplexer. It seamlessly bridges incoming developer queries with OpenRouter's vast ecosystem of cutting-edge models (both free and paid tiers) using the LangChain expression language, allowing dynamic scaling without swapping core application infrastructure.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance asynchronous HTTP web framework routing all API operations. |
| **LangChain** | Core abstraction layer driving prompt templating and LLM invocations. |
| **OpenRouter API** | Remote multiplexer acting as the upstream provider for hundreds of multi-modal foundation models. |
| **PyJWT & OAuth2** | Manages strict bearer-token authentication protecting endpoints from unauthorized access. |
| **PyYAML** | Handles static model mappings and fallback configurations via schema dictionaries. |
| **Docker & GitHub Actions** | Containerizes the entire platform for lightweight, stateless cloud deployment natively piped to Hugging Face Spaces. |

## Technical Architecture

The service runs on a deeply decoupled architectural pipeline to ensure maximum resilience and runtime dynamism. At its core, the **Configuration Engine** (`api_config.py` & `auth_config.py`) securely bootstraps remote credentials and parses baseline model schema arrays. During application boot, the **Dynamic Discovery Engine** (`orouter_inv.py`) probes OpenRouter directly to query real-time model shifts (capturing dynamic pricing or structural context length parameters) and securely caches them directly into the centralized `app.state` pool. 

Incoming HTTP requests are strictly gated by the internal **Security Validator** (`auth.py`) which dynamically issues and verifies stateless JWT payloads via the `/token` endpoint before clearing any subsequent transactions. Once cleared, authorized requests are piped directly into the **LLM Factory** (`llm_loader.py`)— a highly configurable module that verifies repository access arrays and instantly spins up isolated LangChain `ChatOpenAI` classes tailored exactly for OpenRouter endpoints. The factory inherently captures and translates complex multi-layered upstream API issues (like hidden vendor-side 429 rate limits trapped inherently as generic 502s) into clean, transparent HTTP exceptions.

[![API Docs](https://img.shields.io/badge/OpenAPI-View%20Docs-blue?logo=swagger)](https://bfavro73-oroutersrv.hf.space/docs)
