import os
import dill
import mlflow
import pandas as pd
from importlib.metadata import version
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

MODEL_NAME = "risk-scorer"
SCORER_FILE = "risk_scorer_deploy.dill"

class DillScorer(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        import risk_scorer_runtime

        with open(context.artifacts["scorer"], "rb") as file:
            self.scorer = dill.load(file)

    def predict(self, context, model_input, params=None):
        return self.scorer.predict(model_input)

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_registry_uri("http://127.0.0.1:5000")

with open(SCORER_FILE, "rb") as file:
    scorer = dill.load(file)

input_example = pd.read_csv("../data/score.csv")[scorer.features].head(5)
signature = infer_signature(input_example, scorer.predict(input_example))

requirements = [
    f"mlflow=={mlflow.__version__}",
    f"scikit-learn=={version('scikit-learn')}",
    f"catboost=={version('catboost')}",
    f"dill=={version('dill')}",
    f"numpy=={version('numpy')}",
    f"pandas=={version('pandas')}",
]

model_args = {
    "python_model": DillScorer(),
    "artifacts": {"scorer": SCORER_FILE},
    "code_paths": ["risk_scorer_runtime.py"],
    "pip_requirements": requirements,
    "input_example": input_example,
    "signature": signature,
}

if int(mlflow.__version__.split(".")[0]) >= 3:
    model_info = mlflow.pyfunc.log_model(name="risk_scorer", **model_args)
else:
    model_info = mlflow.pyfunc.log_model(artifact_path="risk_scorer", **model_args)

registered = mlflow.register_model(model_info.model_uri, MODEL_NAME)
MlflowClient().set_registered_model_alias(
    MODEL_NAME, "risk_scorer", registered.version
)
print("Registered version:", registered.version)