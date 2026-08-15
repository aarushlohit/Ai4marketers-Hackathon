"""
Model Registry — loads trained ML models from disk/MLflow at startup.
Falls back to untrained placeholder models if saved models not found.
"""

import joblib
import os
import structlog
from pathlib import Path

logger = structlog.get_logger()

MODELS_DIR = Path(__file__).parent.parent.parent / "models" / "saved"


class ModelRegistry:
    _models: dict = {}

    @classmethod
    async def load_all(cls):
        """Load all prediction models at service startup."""
        model_files = {
            "churn": "churn_model.joblib",
            "lead_score": "lead_score_model.joblib",
            "revenue": "revenue_model.joblib",
            "health_score": "health_score_model.joblib",
        }

        for name, filename in model_files.items():
            path = MODELS_DIR / filename
            if path.exists():
                try:
                    cls._models[name] = joblib.load(path)
                    logger.info(f"Loaded model: {name}", path=str(path))
                except Exception as e:
                    logger.warning(f"Failed to load {name}: {e} — using placeholder")
                    cls._models[name] = None
            else:
                logger.warning(f"Model file not found: {filename} — training required")
                cls._models[name] = None

    @classmethod
    def get(cls, name: str):
        return cls._models.get(name)

    @classmethod
    def is_loaded(cls, name: str) -> bool:
        return cls._models.get(name) is not None
