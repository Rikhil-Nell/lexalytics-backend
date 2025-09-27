# Best practice: A .dockerignore file is crucial for keeping the build context small and fast.
# Create a .dockerignore file in the same directory with these contents:
# .venv
# .git
# .pytest_cache
# __pycache__
# *.pyc

ARG UV_VERSION=0.7.18

# --- Stage 1: builder - Install dependencies and the project ---
FROM python:3.13-slim-bookworm AS builder

# Install build-time system dependencies. 'build-essential' is for compiling C extensions if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the pinned version
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies from the lock file into a virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --compile-bytecode

# Copy the entire backend source code
COPY ./backend /app

# Sync the project itself into the environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --compile-bytecode

# --- Stage 2: final - Create a minimal and secure production image ---
FROM python:3.13-slim-bookworm

# <<< FIX: Added WeasyPrint's runtime dependencies here
# These are the libraries WeasyPrint needs to actually run.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libcairo2 \
    libgobject-2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy the virtual environment and source code from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app

# Switch to the non-root user
USER appuser

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]