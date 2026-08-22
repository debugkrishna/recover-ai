import joblib
import pandas as pd


MODEL_PATH = "ml/artifacts/recovery_model.pkl"
PREPROCESSOR_PATH = "ml/artifacts/preprocessor.pkl"


model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


def predict_recovery(payment_data: dict):

    df = pd.DataFrame([payment_data])

    processed_data = preprocessor.transform(df)

    probability = model.predict_proba(
        processed_data
    )[0][1]

    prediction = int(probability >= 0.5)

    return {
        "recovered_prediction": prediction,
        "recovery_probability": round(
            float(probability),
            4,
        ),
    }