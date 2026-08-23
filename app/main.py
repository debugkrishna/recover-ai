from fastapi import FastAPI
from agent.agent import run_agent
from app.schemas import PaymentRequest
from ml.predict import predict_recovery
from agent.tools import (
    get_payment,
    get_customer,
    predict_customer_recovery,
)

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
def predict(payment: PaymentRequest):

    payment_data = get_payment(
        payment.payment_id
    )

    if "error" in payment_data:
        return payment_data

    customer_data = get_customer(
        payment_data["customer_id"]
    )

    if "error" in customer_data:
        return customer_data

    result = predict_customer_recovery(
        payment_data,
        customer_data
    )

    probability = result["recovery_probability"]

    if probability >= 0.80:
        risk_level = "high_recovery"
    elif probability >= 0.50:
        risk_level = "medium_recovery"
    else:
        risk_level = "low_recovery"

    return {
        "payment_id": payment.payment_id,
        "recovery_probability": probability,
        "recovery_prediction": result[
            "recovered_prediction"
        ],
        "recovery_level": risk_level,
    }


@app.post("/agent-recovery")
def agent_recovery(payment: PaymentRequest):

    result = run_agent(
        f"""
        Analyze the failed payment {payment.payment_id}.

        Retrieve the payment and customer information,
        calculate the recovery probability using the ML model,
        choose an appropriate recovery action,
        execute the required tools,
        and provide a concise recovery plan.
        """
    )

    return {
        "payment_id": payment.payment_id,
        "agent_response": result,
    }