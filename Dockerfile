# Multi-stage build to reduce image size
FROM python:3.8-alpine AS builder

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-install-project

# Copy source
COPY main.py devices.json ./

# Final stage
FROM python:3.8-alpine

# Copy the virtual environment from builder
COPY --from=builder /app /app

# Set working directory
WORKDIR /app

# Run the script
CMD ["/app/.venv/bin/python", "main.py"]
