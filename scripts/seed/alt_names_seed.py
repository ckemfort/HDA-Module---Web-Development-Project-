from scripts.seed.utilities import (
    DB_PATH,
    CAT_API_JSON,
    get_connection,
    load_json,
    clean_text,
    split_csv_field,
)

def seed_alt_names(conn=None):
    """
    Seeds breed_alt_names table, inserts (breed_id, alt_name) pairs
    If conn is provided, it will use that connection and will NOT close connection
    If conn is None, it will create/close its own connection
    """
    owns_connection = False
    if conn is None:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}")
        conn = get_connection()
        owns_connection = True

    breeds = load_json(CAT_API_JSON)
    cursor = conn.cursor()

    insert_sql = """
    INSERT OR IGNORE INTO breed_alt_names (
        breed_id,
        alt_name
    ) VALUES (?, ?);
    """

    inserted = 0
    skipped = 0

    for breed in breeds:
        breed_id = clean_text(breed.get("id"))
        if not breed_id:
            skipped += 1
            continue
# creates a list of cleaned alt_names
        alt_names_raw = breed.get("alt_names")
        alt_names = split_csv_field(alt_names_raw)

        for alt in alt_names:
            cursor.execute(insert_sql, (breed_id, alt))
            inserted += 1

    if owns_connection:
        conn.commit()
        conn.close()

    print(f"Alt names processed: inserted={inserted}, skipped_breeds={skipped}")


if __name__ == "__main__":
    seed_alt_names()