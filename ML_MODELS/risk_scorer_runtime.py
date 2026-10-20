import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def lowercase_column(X):
    return X.astype(str).apply(lambda column: column.str.lower())


def replace_rare_values_transformer(X, allowed_values=None, default_value="other"):
    if allowed_values is None:
        return X

    allowed_set = set(allowed_values)
    return X.apply(
        lambda column: column.map(
            lambda value: value if value in allowed_set else default_value
        )
    )


class FeatureMultiplier(BaseEstimator, TransformerMixin):
    def __init__(self, col1, col2, new_col_name):
        self.col1 = col1
        self.col2 = col2
        self.new_col_name = new_col_name

    def fit(self, X, y=None):
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        return self

    def transform(self, X):
        X_out = pd.DataFrame(X).copy()
        values = X_out[self.col1] * X_out[self.col2]
        return pd.DataFrame({self.new_col_name: values}, index=X_out.index)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        return np.asarray([self.new_col_name], dtype=object)


class FeatureDivider(BaseEstimator, TransformerMixin):
    def __init__(self, numerator, denominator, new_col_name, eps=1):
        self.numerator = numerator
        self.denominator = denominator
        self.new_col_name = new_col_name
        self.eps = eps

    def fit(self, X, y=None):
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        return self

    def transform(self, X):
        X_out = pd.DataFrame(X).copy()
        values = X_out[self.numerator] / (X_out[self.denominator] + self.eps)
        return pd.DataFrame({self.new_col_name: values}, index=X_out.index)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        return np.asarray([self.new_col_name], dtype=object)


class PolicyRiskScorer:
    def __init__(self, claim_model, count_model, severity_model, features):
        self.claim_model = claim_model
        self.count_model = count_model
        self.severity_model = severity_model
        self.features = list(features)

    def predict(self, df):
        X = df[self.features]
        claim_estimator = self.claim_model.named_steps["model"]
        positive_index = list(claim_estimator.classes_).index(1)

        claim_probability = self.claim_model.predict_proba(X)[:, positive_index]
        count_if_claim = np.maximum(self.count_model.predict(X), 0)
        avg_loss_if_claim = np.maximum(self.severity_model.predict(X), 0)

        result = df.copy()
        result["claim_probability"] = claim_probability
        result["count_if_claim"] = count_if_claim
        result["avg_loss_if_claim"] = avg_loss_if_claim
        result["expected_claim_count"] = claim_probability * count_if_claim
        result["expected_total_loss"] = (
            result["expected_claim_count"] * result["avg_loss_if_claim"]
        )
        return result
