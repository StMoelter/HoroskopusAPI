from flask import Flask
from flasgger import Swagger


def create_app():
    app = Flask(__name__)
    Swagger(app)

    from .routes import main

    app.register_blueprint(main)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
