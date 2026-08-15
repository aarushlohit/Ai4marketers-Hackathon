# 📈 ML Engine — Miracle Birds

Predictive analytics service for customer intelligence.

## Technology Stack

- **FastAPI** — REST API (port 8002)
- **XGBoost 2.0** — Churn prediction model
- **scikit-learn 1.3** — Lead scoring, health score
- **LightGBM** — Revenue forecasting
- **SHAP** — Model explainability
- **MLflow** — Experiment tracking & model registry

## Prediction Models

| Model               | Algorithm        | Target Metric  |
| ------------------- | ---------------- | -------------- |
| Churn Prediction    | XGBoost          | AUC-ROC > 0.85 |
| Lead Scoring        | Random Forest    | F1 > 0.80      |
| Revenue Forecasting | LightGBM + ARIMA | MAPE < 15%     |
| Health Score        | Ensemble         | MAE < 5 points |

## API Endpoints

```
POST /predict/churn         — Churn probability (0-1)
POST /predict/lead-score    — Lead score (0-100)
POST /predict/revenue       — Revenue forecast
POST /predict/health-score  — Customer health score
POST /batch/refresh-predictions — Batch refresh (Celery)
POST /batch/train/{model}   — Trigger retraining
GET  /health                — Health check
```

## Model Lifecycle

1. Features extracted from PostgreSQL
2. Training via XGBoost/sklearn with MLflow tracking
3. Model saved to `models/saved/` via joblib
4. Loaded at startup by `ModelRegistry`
5. Weekly retraining via Celery beat

## Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```
