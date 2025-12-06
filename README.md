# FastAPI Claude-Proxy Backend

## Project Summary
This project is a clean, professional backend service designed to act as a proxy for the Anthropic Claude API. Built with FastAPI, it aims to provide a robust, scalable, and secure interface for client applications to interact with Claude, featuring streaming support and efficient resource management.

## Goals
- **Secure Proxy**: Hide API keys and manage authentication centrally.
- **Streaming Support**: Enable real-time token streaming from Claude to clients.
- **Scalability**: Designed for deployment on AWS ECS Fargate with load balancing.
- **Maintainability**: Clean architecture with type-safe Python code.

## Architecture
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (via RDS) for persistent storage.
- **Caching/Broker**: Redis (via ElastiCache) for rate limiting and message brokering.
- **Infrastructure**: Dockerized containers running on AWS ECS Fargate behind an Application Load Balancer (ALB).

## Quick Start
1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd <repo-name>
    ```
2.  **Environment Setup**:
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and replace placeholders (e.g., `ANTHROPIC_API_KEY`) with your actual values.
3.  **Run Locally**:
    (Instructions to be added in future steps. Currently, the project is in the skeleton phase.)

## Step 1 Outputs
This repository structure was generated as part of Step 1. It includes:
- Basic directory structure (`src`, `tests`, `infra`, `docs`).
- Configuration files (`pyproject.toml`, `Dockerfile`, `.gitignore`).
- Placeholder source and test files.
