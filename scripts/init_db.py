import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "instance" / "cats.db"

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()

    # Main table
    c.execute("""
    CREATE TABLE IF NOT EXISTS cat_breeds (
        breed_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        origin TEXT, 
        cfa_url TEXT,
        wikipedia_url TEXT,
        featured_image_url TEXT,
        description TEXT,
        hypoallergenic INTEGER,
        weight_min INTEGER,
        weight_max INTEGER,
        life_span_min INTEGER,
        life_span_max INTEGER,
        adaptability INTEGER,
        affection_level INTEGER,
        child_friendly INTEGER,
        dog_friendly INTEGER,
        energy_level INTEGER,
        grooming INTEGER,
        health_issues INTEGER,
        intelligence INTEGER,
        shedding_level INTEGER,
        social_needs INTEGER,
        stranger_friendly INTEGER
    );
    """)

    # Index for name search
    c.execute("CREATE INDEX IF NOT EXISTS idx_cat_breeds_name ON cat_breeds(name);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cat_breeds_origin ON cat_breeds(origin);")


    # Alt names (many per breed)
    c.execute("""
    CREATE TABLE IF NOT EXISTS breed_alt_names (
        breed_id TEXT NOT NULL,
        alt_name TEXT NOT NULL,
        PRIMARY KEY (breed_id, alt_name),
        FOREIGN KEY (breed_id) REFERENCES cat_breeds(breed_id) ON DELETE CASCADE
    );
    """)

    # German info (
    c.execute("""
    CREATE TABLE IF NOT EXISTS breed_de_info (
        breed_id TEXT PRIMARY KEY,
        de_name TEXT NOT NULL,
        de_description TEXT,
        de_wiki_url TEXT,
        FOREIGN KEY (breed_id) REFERENCES cat_breeds(breed_id) ON DELETE CASCADE
    );
    """)

    # Temperament lookup
    c.execute("""
    CREATE TABLE IF NOT EXISTS temperament (
        temperament_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # Junction table m-m
    c.execute("""
    CREATE TABLE IF NOT EXISTS breed_temperament (
        breed_id TEXT NOT NULL,
        temperament_id INTEGER NOT NULL,
        PRIMARY KEY (breed_id, temperament_id),
        FOREIGN KEY (breed_id) REFERENCES cat_breeds(breed_id) ON DELETE CASCADE,
        FOREIGN KEY (temperament_id) REFERENCES temperament(temperament_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print(f"DB initialized at: {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()