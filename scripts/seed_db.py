# Orchestrator to seed the database in the correct order.
# Run from project root:
# python -m scripts.seed_db

from scripts.seed.utilities import get_connection
from scripts.seed.cat_breeds_seed import seed_cat_breeds
from scripts.seed.german_info_seed import seed_breed_de_info
from scripts.seed.temperament_seed import seed_temperament
from scripts.seed.alt_names_seed import seed_alt_names


def main():
    conn = get_connection()
    try:
        # Correct order (parents first)
        seed_cat_breeds(conn)
        seed_breed_de_info(conn)
        seed_temperament(conn)     # seeds temperament + breed_temperament
        seed_alt_names(conn)

        conn.commit()
        print("Seeding complete. Changes committed.")
    except Exception:
        conn.rollback()
        print("Seeding failed. Changes rolled back.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()