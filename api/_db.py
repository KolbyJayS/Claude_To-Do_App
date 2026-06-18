import pg8000.native
from contextlib import contextmanager
from _config import DATABASE_URL
from urllib.parse import urlparse

_parsed = None


def _get_conn_kwargs():
    global _parsed
    if _parsed is None:
        p = urlparse(DATABASE_URL)
        _parsed = {
            "host": p.hostname,
            "port": p.port or 5432,
            "database": p.path.lstrip("/"),
            "user": p.username,
            "password": p.password,
            "ssl_context": True,
        }
    return _parsed


def _connect():
    kwargs = _get_conn_kwargs()
    return pg8000.native.Connection(**kwargs)


def fetchone(sql, params=None):
    conn = _connect()
    try:
        if params:
            rows = conn.run(sql, *params)
        else:
            rows = conn.run(sql)
        cols = [c["name"] for c in conn.columns]
        if not rows:
            return None
        return dict(zip(cols, rows[0]))
    finally:
        conn.close()


def fetchall(sql, params=None):
    conn = _connect()
    try:
        if params:
            rows = conn.run(sql, *params)
        else:
            rows = conn.run(sql)
        cols = [c["name"] for c in conn.columns]
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()


def execute(sql, params=None):
    conn = _connect()
    try:
        if params:
            rows = conn.run(sql, *params)
        else:
            rows = conn.run(sql)
        cols = [c["name"] for c in conn.columns] if conn.columns else []
        if not rows or not cols:
            return None
        return dict(zip(cols, rows[0]))
    finally:
        conn.close()
