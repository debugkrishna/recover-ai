from fastapi import FastAPI

from app.schemas import PaymentData
from ml.predict import predict_recovery


app = FastAPI(
    title="RecoverAI",
    description="AI-powered revenue recovery system",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "RecoverAI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict-recovery")
def predict(payment: PaymentData):

    result = predict_recovery(
        payment.model_dump()
    )

    probability = result["recovery_probability"]

    if probability >= 0.80:
        risk_level = "high_recovery"
    elif probability >= 0.50:
        risk_level = "medium_recovery"
    else:
        risk_level = "low_recovery"

    return {
        "recovery_probability": probability,
        "recovery_prediction": result[
            "recovered_prediction"
        ],
        "recovery_level": risk_level,
    }