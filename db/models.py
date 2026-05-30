import bcrypt

from db.database import get_conn


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_user(username: str, password: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, _hash_password(password)),
        )
        return cur.lastrowid


def get_user_by_username(username: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None


def save_flashcards(user_id: int, topic: str, cards: list[dict]) -> int:
    with get_conn() as conn:
        conn.executemany(
            "INSERT INTO flashcards (user_id, topic, question, answer) VALUES (?, ?, ?, ?)",
            [(user_id, topic, c["question"], c["answer"]) for c in cards],
        )
        return len(cards)


def list_flashcards(user_id: int, topic: str | None = None) -> list[dict]:
    sql = "SELECT id, topic, question, answer, created_at FROM flashcards WHERE user_id = ?"
    params: list = [user_id]
    if topic:
        sql += " AND topic = ?"
        params.append(topic)
    sql += " ORDER BY created_at DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def list_flashcard_topics(user_id: int) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT topic FROM flashcards WHERE user_id = ? ORDER BY topic",
            (user_id,),
        ).fetchall()
        return [r["topic"] for r in rows]


def save_exam(user_id: int, topic: str, difficulty: str, content_md: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO exams (user_id, topic, difficulty, content_md) VALUES (?, ?, ?, ?)",
            (user_id, topic, difficulty, content_md),
        )
        return cur.lastrowid


def list_exams(user_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, topic, difficulty, content_md, created_at "
            "FROM exams WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
