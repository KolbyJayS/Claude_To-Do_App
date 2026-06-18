import psycopg2
import psycopg2.pool
import psycopg2.extras
from contextlib import contextmanager
from _config import DATABASE_URL

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(1, 5, DATABASE_URL)
    return _pool


@contextmanager
def get_db():
    conn = _get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _get_pool().putconn(conn)


def fetchone(sql, params=None):
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def fetchall(sql, params=None):
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql, params=None):
    """Run a DML statement and return the first row (for RETURNING clauses)."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            try:
                return cur.fetchone()
            except psycopg2.ProgrammingError:
                return None
