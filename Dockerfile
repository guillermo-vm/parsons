# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Install uv by copying it from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
# We use --frozen to ensure it matches your local uv.lock exactly
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Run stage
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment and your code from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY . .

# Add the virtual environment to the PATH so 'gunicorn' can be found
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8080
EXPOSE 8080

# Start the app
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]