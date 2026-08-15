"""
SHAP Explainability — generate feature importance explanations for predictions.
Used to produce human-readable "why" for every prediction.
"""

import structlog
import numpy as np

logger = structlog.get_logger()


class SHAPExplainer:
    """
    Wraps SHAP to produce top-N feature explanations for a prediction.
    Falls back to mock explanations if SHAP or the model is not available.
    """

    def __init__(self, model, feature_names: list[str]):
        self.model = model
        self.feature_names = feature_names
        self._explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            import shap
            # TreeExplainer is fastest for XGBoost/sklearn tree models
            clf = self.model.named_steps.get("clf", self.model)
            self._explainer = shap.TreeExplainer(clf)
            logger.info("SHAP TreeExplainer initialized")
        except Exception as e:
            logger.warning("SHAP unavailable — using feature importance fallback",
                           error=str(e))

    def explain(
        self,
        feature_vector: list[float],
        top_n: int = 5,
    ) -> list[dict]:
        """
        Return top-N feature contributions for a single prediction.

        Returns list of dicts:
          [{"name": "days_since_last_interaction", "impact": 0.32}, ...]
        """
        if self._explainer is not None:
            try:
                return self._explain_shap(feature_vector, top_n)
            except Exception as e:
                logger.warning("SHAP explanation failed", error=str(e))

        return self._explain_fallback(feature_vector, top_n)

    def _explain_shap(self, vector: list[float], top_n: int) -> list[dict]:
        import shap
        arr = np.array(vector).reshape(1, -1)

        # Run through scaler if pipeline
        if hasattr(self.model, "named_steps"):
            scaler = self.model.named_steps.get("scaler")
            if scaler:
                arr = scaler.transform(arr)

        shap_values = self._explainer.shap_values(arr)
        values = shap_values[0] if isinstance(shap_values, list) else shap_values[0]

        # Pair feature names with |shap value|
        pairs = sorted(
            zip(self.feature_names, values),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        total = sum(abs(v) for _, v in pairs) or 1.0
        return [
            {"name": name, "impact": round(abs(val) / total, 4)}
            for name, val in pairs[:top_n]
        ]

    def _explain_fallback(self, vector: list[float], top_n: int) -> list[dict]:
        """Fallback: use model feature_importances_ if available."""
        try:
            clf = self.model.named_steps.get("clf", self.model)
            importances = clf.feature_importances_
            pairs = sorted(
                zip(self.feature_names, importances),
                key=lambda x: x[1],
                reverse=True,
            )
            total = sum(imp for _, imp in pairs) or 1.0
            return [
                {"name": name, "impact": round(imp / total, 4)}
                for name, imp in pairs[:top_n]
            ]
        except Exception:
            # Last resort: return named placeholders
            return [
                {"name": f"{fn}", "impact": round(1 / top_n, 4)}
                for fn in (self.feature_names[:top_n] if self.feature_names else
                           ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"])
            ]
