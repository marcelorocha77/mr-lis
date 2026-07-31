FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "."

COPY . .

EXPOSE 8000

# Dev (docker-compose) chama uvicorn direto; prod (Fly.io) usa deploy_start que roda migrations antes.
CMD ["python", "-m", "app.scripts.deploy_start"]
