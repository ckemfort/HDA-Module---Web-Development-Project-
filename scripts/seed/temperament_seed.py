from scripts.seed.utilities import (
    DB_PATH,
    CAT_API_JSON,
    get_connection,
    load_json,
    clean_text,
    split_csv_field,
)


def seed_temperaments(cur, breeds):
    """
    Seeds temperament table unique temperament names
    """
    insert_sql = "INSERT OR IGNORE INTO temperament (name) VALUES (?);"

    for breed in breeds:
        traits = split_csv_field(clean_text(breed.get("temperament")))
        for trait in traits:
            cur.execute(insert_sql, (trait,))


def seed_breed_temperaments(cur, breeds):
    """
    Seeds breed_temperament lookup table with breed - temperament relationships
    """
    select_id_sql = "SELECT temperament_id FROM temperament WHERE name = ?;"
    insert_link_sql = """
        INSERT OR IGNORE INTO breed_temperament (breed_id, temperament_id)
        VALUES (?, ?);
    """

    for breed in breeds:
        breed_id = clean_text(breed.get("id"))
        if not breed_id:
            continue

        traits = split_csv_field(clean_text(breed.get("temperament")))
        for trait in traits:
            cur.execute(select_id_sql, (trait,))
            row = cur.fetchone()
            if not row:
                continue
            cur.execute(insert_link_sql, (breed_id, row[0]))

def seed_temperament(conn=None):
    owns_connection = False
    if conn is None:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}")
        conn = get_connection()
        owns_connection = True


    breeds = load_json(CAT_API_JSON)
    cur = conn.cursor()

    seed_temperaments(cur, breeds)
    seed_breed_temperaments(cur, breeds)

    if owns_connection:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    seed_temperament()