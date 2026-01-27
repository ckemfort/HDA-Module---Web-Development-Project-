from flask import Flask
from pathlib import Path
from db import init_app as init_db
from views import bp as views_bp

def create_app():
    # Path to override default flask behaviour - Flask expects the DB to be inside app directory
    project_root = Path(__file__).resolve().parent.parent

    instance_dir = project_root / "instance"

    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=str(instance_dir),
    )

    app.config["DATABASE"] = "cats.db"

    init_db(app)
    app.register_blueprint(views_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)