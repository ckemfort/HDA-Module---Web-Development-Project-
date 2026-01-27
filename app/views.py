from flask import Blueprint, render_template, request
from db import get_db
from services.cat_api import fetch_gallery_images

bp = Blueprint("views", __name__)

@bp.route("/")
def index():
    db = get_db()

    random_breeds = db.execute("""
        SELECT
            b.breed_id,
            b.name,
            b.featured_image_url
        FROM cat_breeds b
        WHERE b.featured_image_url IS NOT NULL AND b.featured_image_url != ''
        ORDER BY RANDOM()
        LIMIT 6;
    """).fetchall()

    return render_template("index.html", random_breeds=random_breeds)


@bp.route("/breeds")
def breeds_overview():
    db = get_db()

    # --- extract query params ---
    search = request.args.get("search", "").strip()
    hypo = request.args.get("hypoallergenic", "").strip()
    cfa = request.args.get("cfa", "") == "1"
    grooming_high = request.args.get("grooming_high", "") == "1"
    origin = request.args.get("origin", "").strip()
    de_article = request.args.get("de_article", "") == "1"
    sort = (request.args.get("sort", "name_asc") or "name_asc").strip()

    # --- base query ---
    sql = """
        SELECT
            b.breed_id,
            b.name,
            b.featured_image_url,
            b.cfa_url,
            b.hypoallergenic,
            b.grooming,
            b.weight_min,
            b.weight_max,
            b.life_span_min,
            b.life_span_max,
            b.origin,
            d.breed_id,
            d.de_name
        FROM cat_breeds AS b
        LEFT JOIN breed_de_info AS d ON d.breed_id = b.breed_id
    """
    where = []
    params = []

    # --- apply filters if checkbox value is not falsy ---
    if search:
        where.append("(LOWER(b.name) LIKE LOWER(?) OR LOWER(d.de_name) LIKE LOWER(?))")
        like = f"%{search}%"
        params.extend([like, like])

    if hypo:
        where.append("b.hypoallergenic = ?")
        params.append(int(hypo))

    if cfa:
        where.append("b.cfa_url IS NOT NULL")

    if grooming_high:
        where.append("b.grooming >= ?")
        params.append(4)

    if origin:
        where.append("b.origin = ?")
        params.append(origin)

    if de_article:
        where.append("d.breed_id IS NOT NULL")

    if where:
        sql += " WHERE " + " AND ".join(where)

    # --- sorting ---
    if sort == "name_asc":
        sql += " ORDER BY b.name ASC"
    elif sort == "weight_asc":
        sql += " ORDER BY b.weight_max ASC"
    elif sort == "weight_desc":
        sql += " ORDER BY b.weight_max DESC"
    elif sort == "lifespan_desc":
        sql += " ORDER BY b.life_span_max DESC"
    else:
        # base sorting function
        sql += " ORDER BY b.name ASC"

    breeds = db.execute(sql, params).fetchall()
    # Country origin filter
    origins = db.execute("""
        SELECT DISTINCT origin
        FROM cat_breeds
        WHERE origin IS NOT NULL AND origin != ''
        ORDER BY origin ASC;
    """).fetchall()

    return render_template(
        "breeds.html",
        all_breeds=breeds,
        origins=[r["origin"] for r in origins],
        active={
            "search": search,
            "hypoallergenic": hypo,
            "cfa": cfa,
            "grooming_high": grooming_high,
            "origin": origin,
            "de_article": de_article,
            "sort": sort
        }
    )

@bp.route("/breeds/<breed_id>")
# Flask extracts the breed_id
def breed_detail(breed_id):
    db = get_db()

    breed = db.execute("""
        SELECT
            b.*,
            d.de_name,
            d.de_description,
            d.de_wiki_url
        FROM cat_breeds b
        LEFT JOIN breed_de_info d ON d.breed_id = b.breed_id
        WHERE b.breed_id = ?;
    """, (breed_id,)).fetchone()

    if breed is None:
        raise ValueError('This breed does not exist in our database')

    temperaments = db.execute(
    """
    SELECT t.name
    FROM temperament t
    JOIN breed_temperament bt ON bt.temperament_id = t.temperament_id
    WHERE bt.breed_id = ?
    ORDER BY t.name
    """, (breed_id,)).fetchall()

    alt_names = db.execute("""
        SELECT alt_name
        FROM breed_alt_names
        WHERE breed_id = ?
        ORDER BY alt_name;
    """, (breed_id,)).fetchall()

    gallery_images = fetch_gallery_images(breed_id, limit=12)

    return render_template(
        "breed_details.html",
        breed=breed,
        temperaments=temperaments,
        alt_names=alt_names,
        gallery_images=gallery_images
    )

