from threading import Thread

from flask import Flask

from blueprints.music.music import music as music_blueprint
from blueprints.music.play import check_queue_and_play


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(music_blueprint, url_prefix="/music")
    return app


if __name__ == "__main__":
    music_queue = Thread(target=check_queue_and_play)
    music_queue.start()
    app = create_app()
    app.run(host="0.0.0.0")
