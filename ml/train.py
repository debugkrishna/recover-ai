import os

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from sklearn.metrics import average_precision_score

from xgboost import XGBClassifier




DATA_PATH = "data/payments_processed.csv"

df = pd.read_csv(DATA_PATH)


X = df.drop("recovered", axis=1)
y = df["recovered"]



categorical_features = [
    "payment_method",
    "failure_reason",
]

numerical_features = [
    column
    for column in X.columns
    if column not in categorical_features
]



X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)



preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numerical",
            "passthrough",
            numerical_features,
        ),
    ]
)


X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)


model = XGBClassifier(
    n_estimators=500,
    max_depth=4,
    learning_rate=0.03,
    min_child_weight=3,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_alpha=0.1,
    reg_lambda=1.0,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
)


model.fit(
    X_train_processed,
    y_train,
)




y_pred = model.predict(X_test_processed)

y_probability = model.predict_proba(
    X_test_processed
)[:, 1]



accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
)

recall = recall_score(
    y_test,
    y_pred,
)

f1 = f1_score(
    y_test,
    y_pred,
)

roc_auc = roc_auc_score(
    y_test,
    y_probability,
)

average_precision = average_precision_score(
    y_test,
    y_probability,
)

print("\n========== MODEL PERFORMANCE ==========\n")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")
print(f"PR-AUC     : {average_precision:.4f}")

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
    )
)




os.makedirs("ml/artifacts", exist_ok=True)

joblib.dump(
    model,
    "ml/artifacts/recovery_model.pkl",
)

joblib.dump(
    preprocessor,
    "ml/artifacts/preprocessor.pkl",
)

print("\nModel saved .")