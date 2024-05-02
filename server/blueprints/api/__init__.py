from flask import Blueprint

from blueprints.api.spotify.spotify import spotify as spotify_blueprint
from blueprints.api.subsonic.subsonic import subsonic as subsonic_blueprint

api = Blueprint("api", __name__)
api.register_blueprint(subsonic_blueprint, url_prefix="/subsonic")
api.register_blueprint(spotify_blueprint, url_prefix="/spotify")
