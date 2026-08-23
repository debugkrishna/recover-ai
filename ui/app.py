import requests
import streamlit as st

from database import (
    get_payment_history,
    get_payment_details,
)


st.set_page_config(
    page_title="RecoverAI",
    page_icon="💳",
    layout="wide",
)


st.title("💳 RecoverAI")
st.subheader("AI-Powered Revenue Recovery")

st.info(
    "Analyze failed payments and generate "
    "AI-powered recovery actions."
)


payment_id = st.text_input(
    "Payment ID",
    placeholder="PAY_001",
)


# =================================
# ACTION BUTTONS
# =================================

col1, col2 = st.columns(2)

with col1:

    analyze_button = st.button(
        "📊 Analyze Payment",
        use_container_width=True,
    )

with col2:

    agent_button = st.button(
        "🤖 Run AI Recovery",
        use_container_width=True,
    )


# =================================
# ANALYZE PAYMENT
# =================================

if analyze_button:

    if not payment_id:

        st.warning(
            "Please enter a Payment ID."
        )

    else:

        try:

            response = requests.post(
                "http://127.0.0.1:8000/predict-recovery",
                json={
                    "payment_id": payment_id
                },
                timeout=10,
            )

            if response.status_code == 200:

                result = response.json()

                details = get_payment_details(
                    payment_id
                )

                payment_history = get_payment_history(
                    payment_id
                )

                st.success(
                    "Analysis complete!"
                )

                # -----------------------------
                # CUSTOMER & PAYMENT
                # -----------------------------

                if details:

                    st.subheader(
                        "👤 Customer & Payment Details"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.markdown(
                            "### 👤 Customer"
                        )

                        st.write(
                            f"**Name:** "
                            f"{details['customer_name']}"
                        )

                        st.write(
                            f"**Customer ID:** "
                            f"{details['customer_id']}"
                        )

                        st.write(
                            f"**Tenure:** "
                            f"{details['tenure_months']} months"
                        )

                        st.write(
                            f"**Lifetime Value:** "
                            f"₹{details['lifetime_value']:,.0f}"
                        )

                        st.write(
                            f"**Successful Payments:** "
                            f"{details['successful_payments']}"
                        )

                        st.write(
                            f"**Failed Payments:** "
                            f"{details['failed_payments']}"
                        )

                    with col2:

                        st.markdown(
                            "### 💳 Payment"
                        )

                        st.write(
                            f"**Payment ID:** "
                            f"{details['payment_id']}"
                        )

                        st.write(
                            f"**Amount:** "
                            f"₹{details['amount']:,.2f}"
                        )

                        st.write(
                            f"**Status:** "
                            f"{details['status']}"
                        )

                        st.write(
                            f"**Failure Reason:** "
                            f"{details['failure_reason']}"
                        )

                        st.write(
                            f"**Retry Count:** "
                            f"{details['retry_count']}"
                        )

                # -----------------------------
                # ML PREDICTION
                # -----------------------------

                st.subheader(
                    "📊 Recovery Prediction"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Recovery Probability",
                        f"{result['recovery_probability']:.2%}",
                    )

                with col2:

                    st.metric(
                        "Prediction",
                        result["recovery_prediction"],
                    )

                with col3:

                    st.metric(
                        "Recovery Level",
                        result["recovery_level"],
                    )

                # -----------------------------
                # AUDIT TRAIL
                # -----------------------------

                st.subheader(
                    "📋 Recovery Audit Trail"
                )

                if payment_history:

                    st.dataframe(
                        payment_history,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No recovery actions recorded yet."
                    )

            else:

                st.error(
                    f"API error: {response.text}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI. "
                "Make sure uvicorn is running."
            )

        except requests.exceptions.Timeout:

            st.error(
                "The API request timed out."
            )

        except Exception as e:

            st.error(
                f"Unexpected error: {e}"
            )


# =================================
# AI RECOVERY AGENT
# =================================

if agent_button:

    if not payment_id:

        st.warning(
            "Please enter a Payment ID."
        )

    else:

        st.subheader(
            "🤖 AI Recovery Agent"
        )

        with st.spinner(
            "AI agent is investigating the payment..."
        ):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/agent-recovery",
                    json={
                        "payment_id": payment_id
                    },
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.success(
                        "AI recovery analysis completed!"
                    )

                    st.markdown(
                        "### 🧠 Agent Decision"
                    )

                    st.write(
                        result["agent_response"]
                    )

                else:

                    st.error(
                        f"Agent API error: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure uvicorn is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The AI agent request timed out."
                )

            except Exception as e:

                st.error(
                    f"Unexpected error: {e}"
                )