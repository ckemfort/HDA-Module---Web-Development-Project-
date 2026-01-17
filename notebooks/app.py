from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

# Datenbank konfigurieren
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cats.db"
db = SQLAlchemy(app)


# Datenbankmodell
class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    temperament = db.Column(db.String(200))
    adaptability = db.Column(db.Integer)
    indoor = db.Column(db.Boolean)
    image = db.Column(db.String(300))


# JSON einmalig importieren
def import_data():
    if Cat.query.first():
        return

    with open("catAPI_cleaned.json", encoding="utf-8") as f:
        data = json.load(f)

    for c in data:
        cat = Cat(
            name=c["name"],
            description=c.get("description"),
            temperament=c.get("temperament"),
            adaptability=c.get("adaptability"),
            indoor=bool(c.get("indoor")),
            image=c.get("image", {}).get("url")
        )
        db.session.add(cat)

    db.session.commit()


@app.route("/")
def home():
    cats = Cat.query.limit(3).all()
    return render_template("home.html", cats=cats)


@app.route("/overview")
def overview():
    search = request.args.get("search", "")
    indoor = request.args.get("indoor")

    query = Cat.query

    if search:
        query = query.filter(Cat.name.ilike(f"%{search}%"))

    if indoor:
        query = query.filter(Cat.indoor == True)

    cats = query.all()
    return render_template("overview.html", cats=cats)


@app.route("/detail/<int:id>")
def detail(id):
    cat = Cat.query.get_or_404(id)
    return render_template("detail.html", cat=cat)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        import_data()
    app.run(debug=True)
