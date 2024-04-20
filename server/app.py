from threading import Thread

from flask import Flask

from blueprints.music import music, check_queue_and_play

app = Flask(__name__)
app.register_blueprint(music, url_prefix="/music")


@app.route("/")
def index():
    return "Hello, this is the server for Rhea!"


if __name__ == "__main__":
    music_queue = Thread(target=check_queue_and_play)
    music_queue.start()
    app.run(debug=True, host="0.0.0.0")
