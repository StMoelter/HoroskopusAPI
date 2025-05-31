# Python Flask API Skeleton

This is a minimal Python API-only application built with Flask and Swagger (via Flasgger).

## Features

- Flask application factory
- Swagger UI documentation at `/docs`
- Pytest for testing
- GitHub Actions for CI

## Getting Started

### Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the app

```bash
export APP_ENV=development
export PORT=5000
python main.py
```

The API documentation is available at http://localhost:5000/docs

### Running tests

```bash
pytest
```

## Code Formatting

This project uses [Black](https://github.com/psf/black) for code formatting. To check for formatting issues:

```bash
black --check .
```

To format the code:

```bash
black .
```

## Docker

Build and run the Docker container for production:

```bash
docker build -t <your-dockerhub-username>/horoskopusapi:latest .
docker run -e APP_ENV=production -p 5000:5000 <your-dockerhub-username>/horoskopusapi:latest
```

The API will be available at http://localhost:5000.

### Development with Docker Compose

Use Docker Compose to start the application in development mode with the host project directory mounted:

```bash
docker-compose up --build
```

The API will be available at http://localhost:5000, and documentation at http://localhost:5000/docs.
