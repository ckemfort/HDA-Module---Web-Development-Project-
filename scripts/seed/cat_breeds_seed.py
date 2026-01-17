from scripts.seed.utilities import (
    DB_PATH,
    CAT_API_JSON,
    get_connection,
    load_json,
    clean_text,
    parse_range,
    get_featured_image_from_cat_api,
)

def seed_cat_breeds(conn=None):
    """
    Seeds main cat_breeds table
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
    INSERT INTO cat_breeds (
        breed_id,
        name,
        origin,
        wikipedia_url,
        description,
        cfa_url,
        featured_image_url,
        hypoallergenic,
        weight_min,
        weight_max,
        life_span_min,
        life_span_max,
        adaptability,
        affection_level,
        child_friendly,
        dog_friendly,
        energy_level,
        grooming,
        health_issues,
        intelligence,
        shedding_level,
        social_needs,
        stranger_friendly
    ) VALUES (
        :breed_id,
        :name,
        :origin,
        :wikipedia_url,
        :description,
        :cfa_url,
        :featured_image_url,
        :hypoallergenic,
        :weight_min,
        :weight_max,
        :life_span_min,
        :life_span_max,
        :adaptability,
        :affection_level,
        :child_friendly,
        :dog_friendly,
        :energy_level,
        :grooming,
        :health_issues,
        :intelligence,
        :shedding_level,
        :social_needs,
        :stranger_friendly
    )
    ON CONFLICT(breed_id) DO UPDATE SET
        name = excluded.name,
        origin = excluded.origin,
        wikipedia_url = excluded.wikipedia_url,
        description = excluded.description,
        cfa_url = excluded.cfa_url,
        featured_image_url = excluded.featured_image_url,
        hypoallergenic = excluded.hypoallergenic,
        weight_min = excluded.weight_min,
        weight_max = excluded.weight_max,
        life_span_min = excluded.life_span_min,
        life_span_max = excluded.life_span_max,
        adaptability = excluded.adaptability,
        affection_level = excluded.affection_level,
        child_friendly = excluded.child_friendly,
        dog_friendly = excluded.dog_friendly,
        energy_level = excluded.energy_level,
        grooming = excluded.grooming,
        health_issues = excluded.health_issues,
        intelligence = excluded.intelligence,
        shedding_level = excluded.shedding_level,
        social_needs = excluded.social_needs,
        stranger_friendly = excluded.stranger_friendly;
    """

    processed = 0
    for breed in breeds:
        weight_min, weight_max = parse_range(breed.get("metric_weight"))
        life_min, life_max = parse_range(breed.get("life_span"))

        params = {
            "breed_id": clean_text(breed.get("id")),
            "name": clean_text(breed.get("name")),
            "origin": clean_text(breed.get("origin")),
            "wikipedia_url": clean_text(breed.get("wikipedia_url")),
            "description": clean_text(breed.get("description")),
            "cfa_url": clean_text(breed.get("cfa_url")),
            "featured_image_url": get_featured_image_from_cat_api(breed),
            "hypoallergenic": breed.get("hypoallergenic"),
            "weight_min": weight_min,
            "weight_max": weight_max,
            "life_span_min": life_min,
            "life_span_max": life_max,
            "adaptability": breed.get("adaptability"),
            "affection_level": breed.get("affection_level"),
            "child_friendly": breed.get("child_friendly"),
            "dog_friendly": breed.get("dog_friendly"),
            "energy_level": breed.get("energy_level"),
            "grooming": breed.get("grooming"),
            "health_issues": breed.get("health_issues"),
            "intelligence": breed.get("intelligence"),
            "shedding_level": breed.get("shedding_level"),
            "social_needs": breed.get("social_needs"),
            "stranger_friendly": breed.get("stranger_friendly"),
        }

        cursor.execute(insert_sql, params)
        processed += 1

    # , commit only if connection was created
    """
    Cheks if script runned directly or called from orchestrator
    if owns_connections = True -> insert, commit and close 
    if owns_connections = False -> insert, orchestrator have commit and close authority
    """
    if owns_connection:
        conn.commit()
        conn.close()

    print(f"Upserted {processed} rows into cat_breeds")

if __name__ == "__main__":
    seed_cat_breeds()

