from scripts.seed.utilities import (
    DB_PATH,
    GERMAN_JSON,
    get_connection,
    load_json,
    clean_text,
)

def seed_breed_de_info(conn=None):
    """
    Seeds breed_de_info table
    If conn is provided, it will use that connection and will NOT close connection
    If conn is None, it will create/close its own connection
    """
    owns_connection = False
    if conn is None:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}")
        conn = get_connection()
        owns_connection = True

    breeds = load_json(GERMAN_JSON)
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO breed_de_info (breed_id, de_name, de_description, de_wiki_url)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(breed_id) DO UPDATE SET
        de_name = excluded.de_name,
        de_description = excluded.de_description,
        de_wiki_url = excluded.de_wiki_url;
    """

    processed = 0
    skipped = 0

    for breed in breeds:
        breed_id = clean_text(breed.get("catApiId"))
        de_name = clean_text(breed.get("breedName"))
        de_description = clean_text(breed.get("description"))
        de_wiki_url = clean_text(breed.get("wikiUrl"))

        if not breed_id or not de_name:
            skipped += 1
            continue

        cursor.execute(insert_sql, (breed_id, de_name, de_description, de_wiki_url))
        processed += 1

    if owns_connection:
        conn.commit()
        conn.close()

        print(f"German breed info processed={processed}, skipped={skipped}")

if __name__ == "__main__":
    seed_breed_de_info()