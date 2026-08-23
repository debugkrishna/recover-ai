from pydantic import BaseModel


class PaymentRequest(BaseModel):
    payment_id: str