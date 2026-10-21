"""
db_utils.py - reusable database helpers for the ApexPlanet Data Analytics Internship (Task 2).

Works with SQLite out of the box and with PostgreSQL / MySQL by changing the connection URL.

Quick start
-----------
    from db_utils import get_engine, load_csv_to_db, run_script, load_queries, run_query

    engine = get_engine()                                   # SQLite file: data/telco.db
    load_csv_to_db("data/processed/telco_churn_cleaned.csv", "telco_clean", engine)
    run_script("sql/01_setup.sql", engine)
    queries = load_queries("sql/02_queries.sql")
    df = run_query(queries["q09_churn_by_contract"], engine=engine)

    # Parameterised query (safe against SQL injection):
    run_query("SELECT * FROM accounts WHERE contract = :c AND tenure >= :t",
              {"c": "Month-to-month", "t": 12}, engine=engine)

Use PostgreSQL instead of SQLite
--------------------------------
    set DB_URL=postgresql+psycopg2://user:password@localhost:5432/telco     (Windows)
    export DB_URL=postgresql+psycopg2://user:password@localhost:5432/telco  (Mac/Linux)
"""
import os
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "telco.db"


def get_engine(db_url=None):
    """Create a SQLAlchemy engine.

    Priority: the db_url argument > the DB_URL environment variable > local SQLite file.
    """
    url = db_url or os.getenv("DB_URL") or f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    if url.startswith("sqlite:///"):
        Path(url.replace("sqlite:///", "", 1)).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url)


def _engine(engine):
    return engine if engine is not None else get_engine()


def load_csv_to_db(csv_path, table="telco_clean", engine=None, if_exists="replace"):
    """Load a cleaned CSV into a database table. Returns the number of rows loaded."""
    engine = _engine(engine)
    df = pd.read_csv(csv_path)
    with engine.begin() as conn:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
    return len(df)


def _strip_comments(sql):
    """Remove full-line '--' comments (keeps the SQL text clean for execution)."""
    return "\n".join(line for line in sql.splitlines() if not line.strip().startswith("--"))


def split_statements(sql):
    """Split a SQL script into individual statements (script must not contain ';' inside strings)."""
    cleaned = _strip_comments(sql)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def run_script(path, engine=None):
    """Execute every statement in a .sql file (DDL, INSERT, CREATE VIEW, CREATE INDEX...)."""
    engine = _engine(engine)
    statements = split_statements(Path(path).read_text(encoding="utf-8"))
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    return len(statements)


def execute_sql(sql, params=None, engine=None):
    """Run a single statement that returns no rows (CREATE INDEX, DROP INDEX, UPDATE...)."""
    engine = _engine(engine)
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def load_queries(path):
    """Read a .sql file that uses '-- name: <id>' markers and return {id: sql_text}."""
    queries, name, buf = {}, None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^--\s*name:\s*(\w+)\s*$", line)
        if m:
            if name:
                queries[name] = _strip_comments("\n".join(buf)).strip().rstrip(";")
            name, buf = m.group(1), []
        elif name:
            buf.append(line)
    if name:
        queries[name] = _strip_comments("\n".join(buf)).strip().rstrip(";")
    return queries


def run_query(sql, params=None, engine=None):
    """Run a SELECT and return a pandas DataFrame.

    Use named placeholders (:name) plus a params dict - never build SQL with f-strings
    from user input, because that allows SQL injection.
    """
    engine = _engine(engine)
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def explain_query(sql, params=None, engine=None):
    """Show the database's execution plan for a query (EXPLAIN QUERY PLAN on SQLite, EXPLAIN elsewhere)."""
    engine = _engine(engine)
    prefix = "EXPLAIN QUERY PLAN " if engine.dialect.name == "sqlite" else "EXPLAIN "
    with engine.connect() as conn:
        result = conn.execute(text(prefix + sql), params or {})
        return pd.DataFrame(result.fetchall(), columns=list(result.keys()))


def list_tables(engine=None):
    """List tables and views in the database (SQLite / PostgreSQL)."""
    engine = _engine(engine)
    if engine.dialect.name == "sqlite":
        q = "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
    else:
        q = "SELECT table_name AS name, table_type AS type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY 2, 1"
    return run_query(q, engine=engine)
