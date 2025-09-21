FROM python:3.11-slim as builder

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY pyproject.toml setup.py MANIFEST.in README.md LICENSE ./
COPY edix ./edix
COPY frontend_src ./frontend_src

# Build frontend
WORKDIR /app/frontend_src
RUN npm install && npm run build

# Build Python package
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
RUN pip install build
RUN python -m build

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy built wheel from builder
COPY --from=builder /app/dist/*.whl /tmp/

# Install Edix
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["edix", "serve", "--host", "0.0.0.0", "--port", "8000", "--db", "/data/edix.db"]
