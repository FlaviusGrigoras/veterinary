from flask import Flask
from config import ApplicationConfig
from models import db

from routes import auth_bp
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

CORS(app)
db.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api")

with app.app_context():
    db.create_all()


@app.route("/")
def main():
    return "Tetin"


if __name__ == "__main__":
    app.run(debug=True)
