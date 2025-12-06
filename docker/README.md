# Docker Local Development Guide

## Quick Start
1.  **Setup Environment**:
    ```bash
    cp .env.example .env
    # Edit .env with your keys if needed (or use defaults for mock mode)
    ```
2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
3.  **Tail Logs**:
    ```bash
    docker-compose logs -f app
    ```
4.  **Stop & Cleanup**:
    ```bash
    docker-compose down
    # To remove volumes (Redis data): docker-compose down -v
    ```

## Running without Docker
If you prefer running locally with `uvicorn`:
```bash
pip install -r requirements.txt
uvicorn src.app.main:app --reload
```

> **Note**: Never commit your `.env` file to version control.
