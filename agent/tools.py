from database import get_connection


CUSTOMERS = {
    "CUST_001": {
        "customer_id": "CUST_001",
        "name": "Rahul",
        "tenure_months": 24,
        "successful_payments": 23,
        "failed_payments": 1,
        "lifetime_value": 15000,
    },
    "CUST_002": {
        "customer_id": "CUST_002",
        "name": "Priya",
        "tenure_months": 8,
        "successful_payments": 4,
        "failed_payments": 6,
        "lifetime_value": 4500,
    },
}


PAYMENTS = {
    "PAY_001": {
        "payment_id": "PAY_001",
        "customer_id": "CUST_001",
        "amount": 1999,
        "status": "failed",
        "failure_reason": "insufficient_funds",
    },
    "PAY_002": {
        "payment_id": "PAY_002",
        "customer_id": "CUST_002",
        "amount": 4999,
        "status": "failed",
        "failure_reason": "expired_card",
    },
}

#Tools
def get_customer(customer_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            customer_id,
            name,
            tenure_months,
            successful_payments,
            failed_payments,
            lifetime_value
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {
            "error": "Customer not found"
        }

    return {
        "customer_id": row[0],
        "name": row[1],
        "tenure_months": row[2],
        "successful_payments": row[3],
        "failed_payments": row[4],
        "lifetime_value": row[5],
    }

def get_payment(payment_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            payment_id,
            customer_id,
            amount,
            status,
            failure_reason,
            retry_count
        FROM payments
        WHERE payment_id = ?
    """, (payment_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {
            "error": "Payment not found"
        }

    return {
        "payment_id": row[0],
        "customer_id": row[1],
        "amount": row[2],
        "status": row[3],
        "failure_reason": row[4],
        "retry_count": row[5],
    }


from ml.predict import predict_recovery

def predict_customer_recovery(
    payment_data: dict,
    customer_data: dict
):

    failed_payments = customer_data["failed_payments"]
    successful_payments = customer_data["successful_payments"]

    total_payments = (
        failed_payments + successful_payments
    )

    success_rate = (
        successful_payments / total_payments
        if total_payments > 0
        else 0.0
    )

    failure_rate = (
        failed_payments / total_payments
        if total_payments > 0
        else 0.0
    )

    ml_input = {
        "customer_age": 25,

        "customer_tenure_months":
            customer_data["tenure_months"],

        "payment_amount":
            payment_data["amount"],

        "previous_payment_success_rate":
            success_rate,

        "previous_failed_payments":
            failed_payments,

        "days_since_last_payment": 30,

        "payment_method": "upi",

        "failure_reason":
            payment_data["failure_reason"],

        "subscription_age_months":
            customer_data["tenure_months"],

        "customer_lifetime_value":
            customer_data["lifetime_value"],

        "previous_recovery_count": 1,

        "failure_rate":
            failure_rate,

        "customer_reliability_score":
            success_rate *
            customer_data["tenure_months"],

        "recovery_history": 1.0,
    }

    print("\nML INPUT:")
    print(ml_input)

    return predict_recovery(ml_input)


import uuid
from datetime import datetime


def schedule_retry(payment_id: str, hours: int):

    MAX_RETRIES = 2

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT retry_count
        FROM payments
        WHERE payment_id = ?
    """, (payment_id,))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {
            "success": False,
            "error": "Payment not found"
        }

    current_retries = row[0]

    if current_retries >= MAX_RETRIES:
        conn.close()
        return {
            "success": False,
            "error": "Maximum retry limit reached."
        }

    new_retry_count = current_retries + 1

    cursor.execute("""
        UPDATE payments
        SET retry_count = ?
        WHERE payment_id = ?
    """, (new_retry_count, payment_id))

    conn.commit()
    conn.close()

    retry_id = f"RETRY_{uuid.uuid4().hex[:8]}"

    return {
        "success": True,
        "retry_id": retry_id,
        "payment_id": payment_id,
        "scheduled_after_hours": hours,
        "retry_count": new_retry_count,
        "message": "Payment retry scheduled successfully."
    }
def send_notification(
    customer_id: str,
    message: str,
    payment_id: str = None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notifications (
            customer_id,
            payment_id,
            message
        )
        VALUES (?, ?, ?)
    """, (
        customer_id,
        payment_id,
        message
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "payment_id": payment_id,
        "message": "Customer notification sent successfully."
    }

def escalate_case(
    customer_id: str,
    reason: str
):

    case_id = f"CASE_{uuid.uuid4().hex[:8]}"

    return {
        "success": True,
        "case_id": case_id,
        "customer_id": customer_id,
        "reason": reason,
        "status": "escalated",
    }

def log_action(
    customer_id: str,
    action: str,
    reason: str,
    payment_id: str = None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO actions (
            customer_id,
            payment_id,
            action,
            reason
        )
        VALUES (?, ?, ?, ?)
    """, (
        customer_id,
        payment_id,
        action,
        reason
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Recovery action logged successfully.",
        "customer_id": customer_id,
        "payment_id": payment_id,
        "action": action,
    }
