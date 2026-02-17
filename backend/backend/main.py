import flask

from backend import create_app
import flask

from backend import create_app

app = create_app()

@app.route("/")
def index():
    return flask.jsonify({"message": "Hello, World!"})



if __name__ == '__main__':
    app.run(port=5000, debug=True)
