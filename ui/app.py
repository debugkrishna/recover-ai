import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from database import get_payment_history, get_payment_details

# ============================================================
# CONFIG
# ============================================================

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RecoverAI | Revenue Recovery",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "payment_id" not in st.session_state:
    st.session_state.payment_id = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "details" not in st.session_state:
    st.session_state.details = None

if "history" not in st.session_state:
    st.session_state.history = None

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None


# ============================================================
# THEME
# ============================================================

dark = st.session_state.dark_mode

if dark:
    BG = "#0b1020"
    SURFACE = "#121a2b"
    SURFACE_2 = "#182238"
    TEXT = "#f8fafc"
    MUTED = "#a8b2c4"
    BORDER = "#26334a"
    INPUT = "#0f1728"
    HERO = "#111a30"
else:
    BG = "#f6f7fb"
    SURFACE = "#ffffff"
    SURFACE_2 = "#f9fafb"
    TEXT = "#111827"
    MUTED = "#667085"
    BORDER = "#e4e7ec"
    INPUT = "#ffffff"
    HERO = "#111827"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>
    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

   .block-container {{
    max-width: 1380px;
    padding-top: 5.5rem !important;
    padding-bottom: 3rem;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    /* ---------------- Header ---------------- */

    .header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 18px 0;
        border-bottom: 1px solid {BORDER};
        margin-bottom: 22px;
    }}

    .brand-wrap {{
        display: flex;
        align-items: center;
        gap: 13px;
    }}

    .logo {{
        width: 48px;
        height: 48px;
        border-radius: 13px;
        background: linear-gradient(145deg, #4353e8, #2938b7);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 23px;
        font-weight: 800;
        box-shadow: 0 7px 18px rgba(67, 83, 232, .25);
    }}

    .brand {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 850;
        letter-spacing: -1.2px;
        line-height: 1;
    }}

    .brand-ai {{
        color: #4353e8;
    }}

    .tagline {{
        color: {MUTED};
        font-size: 13px;
        margin-top: 5px;
    }}

    .operational {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #ecfdf3;
        color: #087443;
        border: 1px solid #c8f1d8;
        border-radius: 999px;
        padding: 9px 13px;
        font-size: 12px;
        font-weight: 800;
    }}

    .green-dot {{
        width: 8px;
        height: 8px;
        background: #16a34a;
        border-radius: 50%;
    }}

    /* ---------------- Hero ---------------- */

    .hero {{
        background: linear-gradient(135deg, #101827 0%, #17223c 100%);
        border-radius: 21px;
        padding: 34px 38px;
        margin-bottom: 28px;
        border: 1px solid #202b43;
        box-shadow: 0 10px 30px rgba(16, 24, 40, .10);
    }}

    .hero-kicker {{
        color: #8ea0ff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 9px;
    }}

    .hero-title {{
        color: white !important;
        font-size: 30px;
        line-height: 1.2;
        font-weight: 850;
        letter-spacing: -.8px;
        margin: 0;
    }}

    .hero-text {{
        color: #cbd5e1;
        font-size: 15px;
        line-height: 1.6;
        margin-top: 10px;
        max-width: 850px;
    }}

    /* ---------------- Sections ---------------- */

    .section-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 850;
        letter-spacing: .11em;
        text-transform: uppercase;
        margin: 24px 0 9px;
    }}

    /* ---------------- Inputs ---------------- */

    div[data-testid="stTextInput"] label {{
        display: none !important;
    }}

    div[data-testid="stTextInput"] input {{
        min-height: 50px !important;
        height: 50px !important;
        border-radius: 10px !important;
        border: 1px solid {BORDER} !important;
        background: {INPUT} !important;
        color: {TEXT} !important;
        font-size: 16px !important;
        padding: 0 15px !important;
    }}

    div[data-testid="stTextInput"] input::placeholder {{
        color: #98a2b3 !important;
        opacity: 1 !important;
    }}

    /* ---------------- Buttons ---------------- */

    div.stButton > button {{
        min-height: 50px !important;
        height: 50px !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        color: white !important;
        background: #111827 !important;
        border: 1px solid #111827 !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }}

    div.stButton > button:hover {{
        background: #2738c7 !important;
        border-color: #2738c7 !important;
        color: white !important;
    }}

    /* Make every button text explicitly visible */
    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {{
        color: white !important;
        opacity: 1 !important;
    }}

    /* Analyze button */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {{
        background: #4353e8 !important;
        border-color: #4353e8 !important;
    }}

    /* ---------------- Cards ---------------- */

    .card {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(16, 24, 40, .035);
        height: 100%;
    }}

    .card-label {{
        color: {MUTED};
        font-size: 10px;
        font-weight: 850;
        letter-spacing: .10em;
        text-transform: uppercase;
    }}

    .card-value {{
        color: {TEXT};
        font-size: 22px;
        font-weight: 850;
        margin-top: 7px;
    }}

    .card-meta {{
        color: {MUTED};
        font-size: 12px;
        margin-top: 5px;
    }}

    /* ---------------- Metrics ---------------- */

    [data-testid="stMetric"] {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
        padding: 14px !important;
        box-shadow: 0 2px 8px rgba(16, 24, 40, .025);
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT} !important;
    }}

    /* ---------------- Recovery ---------------- */

    .probability {{
        color: {TEXT};
        font-size: 43px;
        font-weight: 850;
        letter-spacing: -1.5px;
        margin-top: 4px;
    }}

    .level {{
        display: inline-block;
        margin-top: 9px;
        padding: 5px 9px;
        border-radius: 7px;
        background: #eef1ff;
        color: #3348c7;
        font-size: 11px;
        font-weight: 850;
    }}

    /* ---------------- Agent ---------------- */

    .agent-panel {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 20px;
    }}

    .agent-title {{
        color: {TEXT};
        font-size: 18px;
        font-weight: 850;
    }}

    .agent-subtitle {{
        color: {MUTED};
        font-size: 13px;
        margin-top: 4px;
    }}

    /* ---------------- Tabs ---------------- */

    button[data-baseweb="tab"] {{
        color: {MUTED} !important;
        font-weight: 750 !important;
    }}

    /* ---------------- Footer ---------------- */

    .footer {{
        border-top: 1px solid {BORDER};
        text-align: center;
        color: #98a2b3;
        font-size: 11px;
        padding-top: 22px;
        margin-top: 40px;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

left, right = st.columns([5, 2])

with left:
    st.markdown(
        """
<div class="header">
    <div class="brand-wrap">
        <div class="logo">₹</div>
        <div>
            <div class="brand">
                Recover<span class="brand-ai">AI</span>
            </div>
            <div class="tagline">
                AI-powered payment revenue recovery
            </div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    status_col, theme_col = st.columns([1.4, 1])

    with status_col:
        st.markdown(
            """
<div style="display:flex; justify-content:flex-end; padding-top:7px;">
    <div class="operational">
        <span class="green-dot"></span>
        System Operational
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with theme_col:
        new_dark = st.toggle(
            "Dark mode",
            value=st.session_state.dark_mode,
            key="theme_toggle",
        )

        if new_dark != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark
            st.rerun()


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-kicker">AI REVENUE RECOVERY</div>
    <div class="hero-title">
        Recover more revenue from failed payments.
    </div>
    <div class="hero-text">
        Predict recovery probability, investigate customer context,
        and let an AI agent execute controlled recovery workflows.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# PAYMENT SEARCH
# ============================================================

st.markdown(
    '<div class="section-label">Analyze a payment</div>',
    unsafe_allow_html=True,
)

input_col, analyze_col, agent_col = st.columns([4.2, 1.15, 1.15])

with input_col:
    payment_id = st.text_input(
        "Payment ID",
        value=st.session_state.payment_id,
        placeholder="PAY_001",
        label_visibility="collapsed",
    ).strip()

with analyze_col:
    analyze_clicked = st.button(
        "📊  Analyze",
        use_container_width=True,
    )

with agent_col:
    agent_clicked = st.button(
        "🤖  Run Agent",
        use_container_width=True,
    )


# ============================================================
# API ACTIONS
# ============================================================

if analyze_clicked:
    if not payment_id:
        st.warning("Enter a payment ID such as PAY_001.")
    else:
        try:
            with st.spinner("Analyzing payment..."):
                response = requests.post(
                    f"{API_BASE}/predict-recovery",
                    json={"payment_id": payment_id},
                    timeout=10,
                )

                if response.status_code != 200:
                    raise RuntimeError(api_error(response, "Prediction API"))

                details = get_payment_details(payment_id)

                if not details:
                    raise RuntimeError(
                        f"No payment details found for {payment_id}."
                    )

                st.session_state.payment_id = payment_id
                st.session_state.analysis = response.json()
                st.session_state.details = details
                st.session_state.history = get_payment_history(payment_id)
                st.session_state.agent_result = None

            st.success("Payment analysis completed.")

        except requests.exceptions.ConnectionError:
            st.error(
                "FastAPI is not running. Start it with: "
                "uvicorn app.main:app --reload"
            )
        except requests.exceptions.Timeout:
            st.error("The prediction request timed out.")
        except Exception as exc:
            st.error(str(exc))


if agent_clicked:
    current_payment = payment_id or st.session_state.payment_id

    if not current_payment:
        st.warning("Analyze a payment first.")
    else:
        try:
            with st.spinner("AI agent is investigating the payment..."):
                response = requests.post(
                    f"{API_BASE}/agent-recovery",
                    json={"payment_id": current_payment},
                    timeout=120,
                )

                if response.status_code != 200:
                    raise RuntimeError(api_error(response, "Agent API"))

                st.session_state.agent_result = response.json()

            st.success("AI recovery workflow completed.")

        except requests.exceptions.ConnectionError:
            st.error(
                "FastAPI is not running. Start it with: "
                "uvicorn app.main:app --reload"
            )
        except requests.exceptions.Timeout:
            st.error("The agent request timed out.")
        except Exception as exc:
            st.error(str(exc))


# ============================================================
# RESULTS
# ============================================================

if st.session_state.analysis and st.session_state.details:

    result = st.session_state.analysis
    details = st.session_state.details
    history = st.session_state.history or []

    # --------------------------------------------------------
    # Payment overview
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">Payment overview</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Payment ID", details["payment_id"])

    with c2:
        st.metric("Amount", f"₹{details['amount']:,.2f}")

    with c3:
        st.metric("Status", str(details["status"]).upper())

    with c4:
        st.metric("Failure Reason", str(details["failure_reason"]))

    # --------------------------------------------------------
    # Recovery intelligence
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">Recovery intelligence</div>',
        unsafe_allow_html=True,
    )

    recovery_col, customer_col = st.columns([1, 1.25])

    with recovery_col:
        probability = float(result["recovery_probability"])
        percent = probability * 100

        st.markdown(
            """
<div class="card">
    <div class="card-label">Recovery probability</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="probability">{percent:.2f}%</div>',
            unsafe_allow_html=True,
        )

        st.progress(max(0.0, min(1.0, probability)))

        st.markdown(
            f'<span class="level">{result["recovery_level"]}</span>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if str(result["recovery_prediction"]) == "1":
            st.success("Model predicts this payment is potentially recoverable.")
        else:
            st.warning("Model predicts a low recovery likelihood.")

    with customer_col:
        st.markdown(
            f"""
<div class="card">
    <div class="card-label">Customer context</div>
    <div class="card-value">{details['customer_name']}</div>
    <div class="card-meta">Customer ID: {details['customer_id']}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric("Tenure", f"{details['tenure_months']} mo")

        with m2:
            st.metric("Successful", details["successful_payments"])

        with m3:
            st.metric("Failed", details["failed_payments"])

        st.caption(
            f"Lifetime value: ₹{details['lifetime_value']:,.0f}  •  "
            f"Retry count: {details['retry_count']}"
        )

    # --------------------------------------------------------
    # Workspace
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">Recovery workspace</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        ["🤖 AI Agent", "📋 Audit Trail", "🔎 Payment Details"]
    )

    with tab1:

        st.markdown(
            """
<div class="agent-panel">
    <div class="agent-title">AI Recovery Agent</div>
    <div class="agent-subtitle">
        Investigate → evaluate → decide → execute → audit
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.agent_result:

            agent_result = st.session_state.agent_result

            st.success("Agent workflow completed.")

            st.markdown("#### Agent decision")

            st.write(
                agent_result.get(
                    "agent_response",
                    "No agent response returned.",
                )
            )

        else:

            st.info(
                "Click **Run Agent** to let the AI agent investigate "
                "the selected payment."
            )

            a, b, c, d = st.columns(4)

            with a:
                st.markdown("**1. Investigate**")
                st.caption("Payment + customer context")

            with b:
                st.markdown("**2. Predict**")
                st.caption("Recovery probability")

            with c:
                st.markdown("**3. Decide**")
                st.caption("Approved recovery action")

            with d:
                st.markdown("**4. Execute**")
                st.caption("Tool + audit log")

    with tab2:

        st.markdown("#### Recovery audit trail")

        if history:
            st.dataframe(
                history,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recovery actions recorded yet.")

    with tab3:

        st.markdown("#### Payment details")

        a, b = st.columns(2)

        with a:
            st.write("**Payment ID:**", details["payment_id"])
            st.write("**Amount:**", f"₹{details['amount']:,.2f}")
            st.write("**Status:**", details["status"])
            st.write("**Failure reason:**", details["failure_reason"])

        with b:
            st.write("**Customer ID:**", details["customer_id"])
            st.write("**Tenure:**", f"{details['tenure_months']} months")
            st.write("**Lifetime value:**", f"₹{details['lifetime_value']:,.0f}")
            st.write("**Retry count:**", details["retry_count"])

else:

    # --------------------------------------------------------
    # Empty state
    # --------------------------------------------------------

    st.markdown(
        f"""
<div class="card" style="margin-top:28px; text-align:center; padding:42px;">
    <div style="font-size:34px;">💳</div>
    <div style="color:{TEXT}; font-size:21px; font-weight:850; margin-top:8px;">
        Ready to analyze a failed payment?
    </div>
    <div style="color:{MUTED}; font-size:14px; margin-top:8px;">
        Enter a payment ID above, such as PAY_001.
    </div>
    <div style="color:{MUTED}; font-size:13px; margin-top:5px;">
        RecoverAI will show payment context, ML recovery probability,
        customer history, AI-agent workflow, and the audit trail.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    RecoverAI · ML prediction + agentic recovery +
    controlled tools + auditability
</div>
""",
    unsafe_allow_html=True,
)
