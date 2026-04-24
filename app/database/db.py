import sqlite3

DB_NAME = "debts_pro.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT UNIQUE,
            language TEXT DEFAULT 'uz',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            second_party_user_id INTEGER,
            second_party_username TEXT,
            person_name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            direction TEXT NOT NULL,
            taken_at TEXT NOT NULL,
            due_at TEXT,
            note TEXT,
            status TEXT DEFAULT 'open',
            confirmation_status TEXT DEFAULT 'self_saved',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            username TEXT,
            full_name TEXT,
            action TEXT,
            message_text TEXT,
            state_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Agar eski baza bo'lsa, yangi ustunlarni qo'shadi
    existing_columns = [row[1] for row in cur.execute("PRAGMA table_info(debts)").fetchall()]

    new_columns = {
        "second_party_user_id": "INTEGER",
        "second_party_username": "TEXT",
        "confirmation_status": "TEXT DEFAULT 'self_saved'"
    }

    for col, col_type in new_columns.items():
        if col not in existing_columns:
            cur.execute(f"ALTER TABLE debts ADD COLUMN {col} {col_type}")

    conn.commit()
    conn.close()


def add_or_update_user(user_id: int, full_name: str, username: str | None):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (user_id, full_name, username)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name = excluded.full_name,
            username = excluded.username
    """, (user_id, full_name, username))

    conn.commit()
    conn.close()


def set_user_lang(user_id: int, lang: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()


def get_user_lang(user_id: int) -> str:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "uz"


def get_user_by_username(username: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id, full_name, username, language FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def save_debt(
    creator_id: int,
    person_name: str,
    amount: float,
    currency: str,
    direction: str,
    taken_at: str,
    due_at: str | None,
    note: str | None,
    second_party_user_id: int | None = None,
    second_party_username: str | None = None,
    confirmation_status: str = "self_saved"
):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO debts (
            creator_id, second_party_user_id, second_party_username,
            person_name, amount, currency, direction,
            taken_at, due_at, note, status, confirmation_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
    """, (
        creator_id,
        second_party_user_id,
        second_party_username,
        person_name,
        amount,
        currency,
        direction,
        taken_at,
        due_at,
        note,
        confirmation_status
    ))

    debt_id = cur.lastrowid
    conn.commit()
    conn.close()
    return debt_id


def update_confirmation_status(debt_id: int, confirmation_status: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE debts
        SET confirmation_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (confirmation_status, debt_id))
    conn.commit()
    conn.close()


def get_debt_by_id(debt_id: int):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, creator_id, second_party_user_id, second_party_username,
               person_name, amount, currency, direction, taken_at, due_at,
               note, status, confirmation_status
        FROM debts
        WHERE id = ?
    """, (debt_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_open_debts_by_direction(user_id: int, direction: str):
    conn = connect()
    cur = conn.cursor()

    opposite = "borrowed" if direction == "lent" else "lent"

    cur.execute("""
        SELECT person_name, amount, currency, taken_at, due_at, note, confirmation_status
        FROM debts
        WHERE status = 'open'
          AND (
              (creator_id = ? AND direction = ?)
              OR
              (second_party_user_id = ? AND direction = ?)
          )
        ORDER BY created_at DESC
    """, (user_id, direction, user_id, opposite))

    rows = cur.fetchall()
    conn.close()
    return rows
def log_action(
    user_id: int | None,
    chat_id: int | None,
    username: str | None,
    full_name: str | None,
    action: str,
    message_text: str | None,
    state_name: str | None
):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO audit_logs (
            user_id, chat_id, username, full_name,
            action, message_text, state_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        chat_id,
        username,
        full_name,
        action,
        message_text,
        state_name
    ))

    conn.commit()
    conn.close()
def search_open_debts(user_id: int, direction: str, search_text: str):
    conn = connect()
    cur = conn.cursor()

    opposite = "borrowed" if direction == "lent" else "lent"

    search_clean = search_text.strip().replace("@", "").lower()
    like_value = f"%{search_clean}%"

    cur.execute("""
        SELECT person_name, amount, currency, taken_at, due_at, note, confirmation_status
        FROM debts
        WHERE status = 'open'
          AND (
              (creator_id = ? AND direction = ?)
              OR
              (second_party_user_id = ? AND direction = ?)
          )
          AND (
              LOWER(person_name) LIKE ?
              OR LOWER(REPLACE(COALESCE(second_party_username, ''), '@', '')) LIKE ?
          )
        ORDER BY created_at DESC
    """, (user_id, direction, user_id, opposite, like_value, like_value))

    rows = cur.fetchall()
    conn.close()
    return rows
def get_admin_stats():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM debts")
    debts_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM debts WHERE confirmation_status = 'pending'")
    pending_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM debts WHERE confirmation_status = 'confirmed'")
    confirmed_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM debts WHERE confirmation_status = 'rejected'")
    rejected_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs")
    logs_count = cur.fetchone()[0]

    conn.close()

    return {
        "users_count": users_count,
        "debts_count": debts_count,
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
        "rejected_count": rejected_count,
        "logs_count": logs_count,
    }


def get_last_users(limit=10):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, full_name, username, language, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_last_logs(limit=10):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, full_name, message_text, state_name, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return rows
def get_pending_debts_for_user(user_id: int):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, creator_id, person_name, amount, currency, direction, taken_at, due_at, note
        FROM debts
        WHERE second_party_user_id = ?
          AND confirmation_status = 'pending'
          AND status = 'open'
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return rows