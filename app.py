import os
import pathlib
from flask import Flask, logging
from config.config import Config
from flask_migrate import Migrate

from modules.web_application.api.api import api
from modules.web_application.models.models import db
from flask_wtf.csrf import CSRFProtect

from modules.web_application.views.views import views


def create_app():
    app = Flask(__name__, template_folder='modules/web_application/templates')

    app.config.from_object(Config)
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_ENABLED'] = False

    @app.route('/routes', methods=['GET'])
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.rule} -> {rule.methods}")
        return "<br>".join(routes)

    db.init_app(app)
    migrate = Migrate(app, db)
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')

    return app

GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

from google_auth_oauthlib.flow import Flow
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

if __name__ == "__main__":
    app.run(debug=True)
