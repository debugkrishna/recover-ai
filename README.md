# RecoverAI 💳

> AI-powered payment revenue recovery system using machine learning, agentic AI, FastAPI, Streamlit, and SQLite.

RecoverAI analyzes failed payments, predicts the probability of successful recovery, and uses an AI agent to investigate the payment, choose appropriate recovery actions, execute approved tools, and maintain an audit trail.

## 🎯 Problem

Failed payments cause revenue leakage for subscription and payment businesses.

A recovery system needs to answer:

- Why did the payment fail?
- How likely is it to be recovered?
- Should the payment be retried?
- When should it be retried?
- Should the customer be notified?
- When should the case be escalated?
- How should every action be recorded?

RecoverAI automates this workflow.

## 💡 Solution

RecoverAI combines:

1. **Machine Learning** — predicts payment recovery probability.
2. **AI Agent** — investigates payment and customer context.
3. **Tool Calling** — lets the agent interact with controlled application tools.
4. **SQLite** — stores customers, payments, retries, notifications, and audit logs.
5. **FastAPI** — exposes prediction and agent APIs.
6. **Streamlit** — provides an interactive dashboard.

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │    Streamlit     │
                         │    Dashboard     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌──────────────┐          ┌────────────────┐
             │  XGBoost ML  │          │  OpenAI Agent  │
             │    Model     │          │                │
             └──────┬───────┘          └───────┬────────┘
                    │                          │
                    │                   ┌──────┴───────┐
                    │                   │    Tools     │
                    │                   └──────┬───────┘
                    │                          │
                    └────────────┬─────────────┘
                                 ▼
                         ┌──────────────────┐
                         │      SQLite      │
                         │     Database     │
                         └──────────────────┘
```

## 🤖 Agent Workflow

For a failed payment such as `PAY_001`:

```text
Payment ID
    │
    ▼
get_payment()
    │
    ▼
get_customer()
    │
    ▼
predict_customer_recovery()
    │
    ▼
Recovery Probability
    │
    ▼
Policy / Agent Decision
    │
    ├── schedule_retry()
    │
    ├── send_notification()
    │
    ├── escalate_case()
    │
    └── log_action()
```

The LLM does not directly manipulate the database. It requests controlled tools, which execute application logic and persist the resulting actions.

## 🧠 Machine Learning

RecoverAI uses an XGBoost classification pipeline for recovery prediction.

### Features

The model uses features including:

- Customer age
- Customer tenure
- Payment amount
- Previous payment success rate
- Previous failed payments
- Days since last payment
- Payment method
- Failure reason
- Subscription age
- Customer lifetime value
- Previous recovery count
- Failure rate
- Customer reliability score
- Recovery history

### Example Prediction

For `PAY_001`:

```text
Recovery Probability: 57.76%
Prediction:           1
Recovery Level:       medium_recovery
```

## 📊 Model Performance

Current evaluation:

| Metric | Score |
|---|---:|
| Accuracy | 69.50% |
| Precision | 55.26% |
| Recall | 35.32% |
| F1 Score | 43.10% |
| ROC-AUC | 70.59% |
| PR-AUC | 51.65% |

Accuracy is not treated as the only metric because recovery prediction is a business decision problem involving class imbalance and different costs for false positives and false negatives.

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- SQLite

### Machine Learning
- Scikit-learn
- XGBoost
- Pandas
- NumPy
- Joblib

### AI
- OpenAI API
- OpenAI Responses API
- Function/tool calling

### Frontend
- Streamlit

### Development
- Git
- GitHub
- Python virtual environment

## 🔧 Agent Tools

The AI agent can use:

```text
get_payment()
get_customer()
predict_customer_recovery()
schedule_retry()
send_notification()
escalate_case()
log_action()
```

These tools allow the agent to perform controlled application actions instead of only generating text.

## 🗄️ Database

RecoverAI uses SQLite to maintain application state.

The database stores information about:

- Customers
- Payments
- Retry attempts
- Notifications
- Recovery actions

Recovery actions are linked to the relevant payment and customer, creating an auditable workflow.

## 🛡️ Safety & Guardrails

RecoverAI uses a controlled tool-based architecture:

```text
LLM
 ↓
Tool request
 ↓
Policy validation
 ↓
Application tool
 ↓
SQLite
```

This keeps the model separate from direct database operations and provides a place to enforce business rules before actions are executed.

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/debugkrishna/recover-ai.git
cd recover-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` or expose your API key.

## ▶️ Start FastAPI

From the project root:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## ▶️ Start Streamlit

In another terminal:

```bash
PYTHONPATH=. streamlit run ui/app.py
```

Enter a payment ID such as:

```text
PAY_001
```

The dashboard provides:

- Customer information
- Payment information
- Recovery probability
- Recovery level
- Recovery audit trail
- AI recovery workflow

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

Example:

```json
{
  "status": "healthy"
}
```

### ML Prediction

```http
POST /predict-recovery
```

Request:

```json
{
  "payment_id": "PAY_001"
}
```

Example response:

```json
{
  "payment_id": "PAY_001",
  "recovery_probability": 0.5776,
  "recovery_prediction": 1,
  "recovery_level": "medium_recovery"
}
```

### AI Recovery

```http
POST /agent-recovery
```

Request:

```json
{
  "payment_id": "PAY_001"
}
```

The agent investigates the payment, evaluates recovery likelihood, chooses recovery actions, executes approved tools, and returns a recovery plan.

## 💳 Example Recovery Flow

Example payment:

```text
Payment ID: PAY_001
Customer: Rahul
Amount: ₹1,999
Status: failed
Failure: insufficient_funds
```

Customer history:

```text
Tenure: 24 months
Successful payments: 23
Failed payments: 1
Lifetime value: ₹15,000
```

Model result:

```text
Recovery probability: 57.76%
```

Agent actions:

```text
1. Schedule retry in 24 hours
2. Notify customer
3. Log recovery action
```

Example final outcome:

```text
Recovery decision:
Retry + customer notification

Retry:
24 hours

Audit:
Action recorded in SQLite
```

## 📁 Project Structure

```text
RecoverAI/
│
├── agent/
│   ├── agent.py
│   ├── policy.py
│   ├── prompts.py
│   └── tools.py
│
├── app/
│   ├── main.py
│   └── schemas.py
│
├── ml/
│   ├── train.py
│   ├── predict.py
│   ├── features.py
│   ├── evaluate.py
│   └── artifacts/
│       ├── recovery_model.pkl
│       └── preprocessor.pkl
│
├── ui/
│   └── app.py
│
├── database.py
├── recoverai.db
├── requirements.txt
├── .gitignore
└── README.md
```

## 🧪 Testing the System

### Test the API health endpoint

```bash
curl http://127.0.0.1:8000/health
```

### Test ML prediction

```bash
curl -X POST http://127.0.0.1:8000/predict-recovery \
-H "Content-Type: application/json" \
-d '{"payment_id":"PAY_001"}'
```

### Run the agent

```bash
python -m agent.agent
```

The agent should investigate the payment, call the appropriate tools, and return a recovery plan.

## 🔮 Future Improvements

- Real payment gateway integration
- Production notification providers
- Automated retry scheduling
- Customer segmentation
- Model monitoring
- Recovery strategy A/B testing
- Model explainability
- PostgreSQL for production
- Authentication and authorization
- Docker deployment
- Cloud deployment
- Recovery revenue analytics
- Better temporal features from real payment history
- Automated evaluation and regression tests

## 🎯 Why RecoverAI?

RecoverAI demonstrates an end-to-end AI engineering workflow:

```text
Data
 ↓
Machine Learning
 ↓
Prediction API
 ↓
AI Agent
 ↓
Tool Calling
 ↓
Business Rules
 ↓
Database
 ↓
Action
 ↓
Audit Trail
```

The project focuses on a working AI system rather than an isolated ML model.

It demonstrates how a predictive model can be embedded inside an agentic workflow that takes controlled, auditable business actions.

## 👨‍💻 Author

**Krishna Arun Magotra**

Information Technology  
NIT Srinagar

GitHub: https://github.com/debugkrishna

## 📌 Project Status

```text
✅ ML recovery model
✅ Model persistence
✅ FastAPI API
✅ SQLite database
✅ AI agent
✅ OpenAI tool calling
✅ Recovery tools
✅ Policy / guardrails
✅ Retry scheduling
✅ Customer notifications
✅ Audit logging
✅ Streamlit dashboard
✅ GitHub documentation
```

More production-oriented features are planned.
