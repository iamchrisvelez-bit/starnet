FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PYTHONPATH=/app/libs/tf_models:/app/libs/tf_journal:/app/libs/tf_bus:/app/libs/tf_config:/app/services/data:/app/services/execution:/app/services/risk:/app/services/compliance:/app/services/comms:/app/services/console_api:/app/services/scheduler
ENV TF_ROOT=/app
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "tf_console.api:app", "--host", "0.0.0.0", "--port", "8080"]
