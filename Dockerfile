# Build stage: install dependencies with uv
FROM python:3.12-slim AS builder

WORKDIR /build

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Create venv and install dependencies
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv --no-cache-dir .

# Runtime stage: minimal image with only runtime dependencies
FROM python:3.12-alpine

WORKDIR /app

# Copy only the virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY main.py .

# Set environment to use the venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Create output directory
RUN mkdir -p output

# Run the script
ENTRYPOINT ["/opt/venv/bin/python", "main.py"]
