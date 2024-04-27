from threading import Thread

from flasgger import Swagger
from flask import Flask

from blueprints.api import api as api_blueprint
from blueprints.api.subsonic.play import check_queue_and_play


def create_app() -> Flask:
    app = Flask(__name__)
    swagger = Swagger(app)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    return app


if __name__ == "__main__":
    music_queue = Thread(target=check_queue_and_play)
    music_queue.start()
    app = create_app()
    app.run(host="0.0.0.0")
