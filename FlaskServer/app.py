from flask import *


app = Flask(__name__)


@app.route("/api/v1/add_event", methods=["POST"])
def add_event():
    date = request.json["date"]
    type = request.json["type"]
    severity = request.json["severity"]


if __name__ == "__main__":
    app.run(debug=True)
