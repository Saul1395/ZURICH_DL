import os
from functools import lru_cache

import mlflow
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

FEATURES = [
    "coverage_type",
    "vehicle_count",
    "vehicle_avg_age",
    "driver_count",
    "driver_avg_age",
    "years_in_business",
    "prior_year_mileage_000",
    "business_type",
    "state",
    "prior_apd_claim_count",
    "prior_al_claim_count",
    "prior_loss_amount",
    "num_heavy_vehicles",
]

PREDICTION_COLUMNS = [
    "claim_probability",
    "count_if_claim",
    "avg_loss_if_claim",
    "expected_claim_count",
    "expected_total_loss",
]


@lru_cache(maxsize=1)
def load_model():
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    model_uri = os.environ.get(
        "MODEL_URI",
        "models:/risk-scorer@risk_scorer",
    )
    return mlflow.pyfunc.load_model(model_uri)


@app.get("/health")
def health():
    try:
        load_model()
    except Exception as error:
        return jsonify({"status": "unavailable", "error": str(error)}), 503
    return jsonify({"status": "ok"})


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("policies"), list):
        return jsonify({"error": "Expected JSON with a 'policies' list."}), 400

    policies = payload["policies"]
    if not policies or not all(isinstance(policy, dict) for policy in policies):
        return jsonify({"error": "'policies' must contain one or more objects."}), 400

    missing = sorted({feature for feature in FEATURES if any(feature not in policy for policy in policies)})
    if missing:
        return jsonify({"error": "Missing required features.", "features": missing}), 400

    model_input = pd.DataFrame(policies, columns=FEATURES)
    predictions = load_model().predict(model_input)
    if not isinstance(predictions, pd.DataFrame):
        return jsonify({"error": "Registered model returned an unexpected output format."}), 500

    return jsonify({
        "predictions": predictions[PREDICTION_COLUMNS].to_dict(orient="records")
    })
