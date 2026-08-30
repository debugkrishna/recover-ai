import sqlite3

DB_PATH = "recoverai.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            tenure_months INTEGER,
            successful_payments INTEGER,
            failed_payments INTEGER,
            lifetime_value REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            amount REAL,
            status TEXT,
            failure_reason TEXT,
            retry_count INTEGER DEFAULT 0,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            payment_id TEXT,
            action TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        payment_id TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO customers
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "CUST_001",
        "Rahul",
        24,
        23,
        1,
        15000
    ))

    cursor.execute("""
        INSERT OR REPLACE INTO customers
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "CUST_002",
        "Priya",
        8,
        4,
        6,
        4500
    ))

    cursor.execute("""
        INSERT OR REPLACE INTO payments
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PAY_001",
        "CUST_001",
        1999,
        "failed",
        "insufficient_funds",
        0
    ))

    cursor.execute("""
        INSERT OR REPLACE INTO payments
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PAY_002",
        "CUST_002",
        4999,
        "failed",
        "expired_card",
        0
    ))

    conn.commit()
    conn.close()


init_db()
seed_data()

if __name__ == "__main__":
    print("RecoverAI database initialized and seeded.")
    

def get_payment_history(payment_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            payment_id,
            action,
            reason,
            timestamp
        FROM actions
        WHERE payment_id = ?
        ORDER BY timestamp DESC
    """, (payment_id,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "payment_id": row[1],
            "action": row[2],
            "reason": row[3],
            "timestamp": row[4],
        }
        for row in rows
    ]

def get_payment_details(payment_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.payment_id,
            p.customer_id,
            p.amount,
            p.status,
            p.failure_reason,
            p.retry_count,
            c.name,
            c.tenure_months,
            c.successful_payments,
            c.failed_payments,
            c.lifetime_value
        FROM payments p
        JOIN customers c
            ON p.customer_id = c.customer_id
        WHERE p.payment_id = ?
    """, (payment_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "payment_id": row[0],
        "customer_id": row[1],
        "amount": row[2],
        "status": row[3],
        "failure_reason": row[4],
        "retry_count": row[5],
        "customer_name": row[6],
        "tenure_months": row[7],
        "successful_payments": row[8],
        "failed_payments": row[9],
        "lifetime_value": row[10],
    }