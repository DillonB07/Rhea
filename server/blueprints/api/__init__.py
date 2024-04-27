from flask import Blueprint

from blueprints.api.subsonic.subsonic import subsonic as subsonic_blueprint

api = Blueprint("api", __name__)
api.register_blueprint(subsonic_blueprint, url_prefix="/subsonic")
