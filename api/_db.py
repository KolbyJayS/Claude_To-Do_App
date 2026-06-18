import re
import pg8000.dbapi
from _config import DATABASE_URL
from urllib.parse import urlparse


def _parse_url():
    p = urlparse(DATABASE_URL)
    return {
        "host": p.hostname,
        "port": p.port or 5432,
        "database": p.path.lstrip("/"),
        "user": p.username,
        "password": p.password,
        "ssl_context": True,
    }


def _connect():
    return pg8000.dbapi.connect(**_parse_url())


def _to_pg8000(sql):
    """Convert %s placeholders to $1, $2, ... for pg8000."""
    i = 0
    def replacer(m):
        nonlocal i
        i += 1
        return f"${i}"
    return re.sub(r'%s', replacer, sql)


def fetchone(sql, params=None):
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(_to_pg8000(sql), params)
        cols = [d[0] for d in cur.description] if cur.description else []
        row = cur.fetchone()
        conn.commit()
        return dict(zip(cols, row)) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetchall(sql, params=None):
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(_to_pg8000(sql), params)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        conn.commit()
        return [dict(zip(cols, row)) for row in rows]
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(sql, params=None):
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(_to_pg8000(sql), params)
        cols = [d[0] for d in cur.description] if cur.description else []
        row = cur.fetchone() if cols else None
        conn.commit()
        return dict(zip(cols, row)) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
