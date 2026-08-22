from pydantic import BaseModel


class PaymentData(BaseModel):
    customer_age: int
    customer_tenure_months: int
    payment_amount: float

    previous_payment_success_rate: float
    previous_failed_payments: int
    days_since_last_payment: int

    payment_method: str
    failure_reason: str

    subscription_age_months: int
    customer_lifetime_value: float
    previous_recovery_count: int

    failure_rate: float
    customer_reliability_score: float
    recovery_history: float