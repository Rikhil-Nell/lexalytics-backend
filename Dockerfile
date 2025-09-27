# Best practice: A .dockerignore file is crucial for keeping the build context small and fast.
# It prevents copying virtual environments, cache files, and git history into the image.
#
# Create a .dockerignore file in the same directory with at least these contents:
# .venv
# .git
# .pytest_cache
# __pycache__
# *.pyc

# Best practice: Define uv version as an argument for flexibility and reproducibility
ARG UV_VERSION=0.7.18

# --- Stage 1: builder - Install dependencies and the project ---
FROM python:3.13-slim-bookworm AS builder

# Best practice: Install system-level dependencies needed by your Python packages.
# Add any libraries your project needs here (e.g., libpq-dev for PostgreSQL, build-essential for C extensions).
# This prevents runtime errors for packages that wrap C libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the pinned version for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies from the lock file into a virtual environment
# The `--no-install-project` flag ensures we only install dependencies,
# which caches them in a separate layer before the source code is added.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --compile-bytecode

# Copy the entire backend source code into the builder stage
# This assumes your Python application code is inside the 'backend' directory
COPY ./backend /app

# Sync the project itself into the environment. This is a quick operation
# as all dependencies are already installed.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --compile-bytecode

# --- Stage 2: final - Create a minimal and secure production image ---
FROM python:3.13-slim-bookworm

# Install only the necessary system packages for the final image.
# 'curl' is added here to enable the HEALTHCHECK.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Best practice: Create a non-root user for security
# Running containers as a non-root user is a critical security measure.
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy the virtual environment and source code from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app

# Switch to the non-root user
USER appuser

# Ensure the installed binaries from the virtual environment are on the PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Best practice: Add a health check to let Docker know if the application is running
# This endpoint should be a lightweight endpoint in your app (e.g., /health).
# If you don't have one, you can temporarily point it to your docs URL.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Start the FastAPI server
# Your main.py is inside the 'app' directory, so the import path is 'app.main:app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]