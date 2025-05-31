from flask import Blueprint, jsonify

main = Blueprint("main", __name__)


@main.route("/hello", methods=["GET"])
def hello():
    """
    A hello world endpoint.
    ---
    responses:
      200:
        description: Greeting message
        schema:
          type: object
          properties:
            message:
              type: string
              example: Hello, World!
    """
    return jsonify({"message": "Hello, World!"})
