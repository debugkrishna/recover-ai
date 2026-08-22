import numpy as np
import pandas as pd

np.random.seed(42)

N = 10000

data = pd.DataFrame({
    "customer_age": np.random.randint(18, 70, N),

    "customer_tenure_months": np.random.randint(1, 60, N),

    "payment_amount": np.round(
        np.random.lognormal(mean=7.0, sigma=0.7, size=N),
        2
    ),

    "previous_payment_success_rate": np.round(
        np.random.uniform(0.4, 1.0, N),
        2
    ),

    "previous_failed_payments": np.random.poisson(1.5, N),

    "days_since_last_payment": np.random.randint(1, 90, N),

    "payment_method": np.random.choice(
        ["card", "upi", "netbanking", "wallet"],
        N,
        p=[0.45, 0.35, 0.10, 0.10]
    ),

    "failure_reason": np.random.choice(
        [
            "insufficient_funds",
            "card_declined",
            "network_error",
            "expired_card",
            "bank_error"
        ],
        N,
        p=[0.30, 0.25, 0.15, 0.10, 0.20]
    ),

    "subscription_age_months": np.random.randint(1, 48, N),

    "customer_lifetime_value": np.round(
        np.random.lognormal(mean=8.5, sigma=0.8, size=N),
        2
    ),

    "previous_recovery_count": np.random.poisson(0.8, N)
})



score = (
    2.8 * (data["previous_payment_success_rate"] - 0.70)
    - 0.35 * data["previous_failed_payments"]
    - 0.018 * data["days_since_last_payment"]
    + 0.20 * data["previous_recovery_count"]
    + 0.015 * data["customer_tenure_months"]
)


score += data["failure_reason"].map({
    "insufficient_funds": -0.35,
    "card_declined": -0.60,
    "network_error": 0.45,
    "expired_card": -0.80,
    "bank_error": 0.15
})

score -= 0.00003 * data["payment_amount"]


score += 0.00001 * data["customer_lifetime_value"]

score += np.random.normal(0, 0.45, N)

probability = 1 / (1 + np.exp(-score))


data["recovered"] = np.random.binomial(
    1,
    probability
)

data.to_csv("data/payments.csv", index=False)

print("Dataset generated successfully!")
print(f"Rows: {len(data)}")
print(f"Columns: {len(data.columns)}")
print("\nRecovery distribution:")
print(data["recovered"].value_counts(normalize=True))

print("\nFirst 5 rows:")
print(data.head())