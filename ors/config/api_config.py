import os, yaml
from dataclasses import dataclass
from typing import Dict, List
from ors.utils.logging_utils import (
    get_logger, set_log_level, DEBUG
)

log = get_logger(__name__)
set_log_level(DEBUG)

@dataclass
class ModelInfo:
    id: str
    tier: str
    context: int | None = None

def load_model_repo(path: str) -> Dict[str, List[ModelInfo]]:
    log.debug(f"Loading model repository from {path}")
    raw = yaml.safe_load(open(path, "r", encoding="utf-8"))
    repo: Dict[str, List[ModelInfo]] = {}
    for provider, models in raw.items():
        repo[provider] = [
            ModelInfo(
                id=m["id"],
                tier=m.get("tier", "free"),
                context=m.get("context"),
            )
            for m in models
        ]
    return repo
    
current_dir = os.path.dirname(os.path.abspath(__file__))
free_model_repo = load_model_repo(os.path.join(current_dir, "free_models.yaml"))
paid_model_repo = load_model_repo(os.path.join(current_dir, "paid_models.yaml"))
