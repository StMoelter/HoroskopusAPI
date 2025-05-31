from app.api import create_app

app = create_app()

if __name__ == "__main__":
    import os

    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("PORT", 5000))
    if env in ("production", "prod"):
        os.execvp("gunicorn", ["gunicorn", "main:app", "--bind", f"0.0.0.0:{port}"])
    else:
        app.run(host="0.0.0.0", port=port, debug=True)