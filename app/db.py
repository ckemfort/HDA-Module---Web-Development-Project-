import sqlite3
from flask import current_app, g
from pathlib import Path

#db connection function
def get_db():
    if "db" not in g:
        instance_path = Path(current_app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
        #Path to db
        db_path = instance_path / current_app.config["DATABASE"]

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        # SAFETY CHECK
        row = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='cat_breeds';"
        ).fetchone()

        if row is None:
            raise RuntimeError(
                f"Database at {db_path} has no cat_breeds table. Wrong DB file?"
            )

        g.db = conn

    return g.db

# close connection
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

