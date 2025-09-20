# Dockerfile
```dockerfile
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
```

# docker-compose.yml
```yaml
version: '3.8'

services:
  edix:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - edix_data:/data
      - ./config/edix.yaml:/app/edix.yaml:ro
    environment:
      - EDIX_DB_PATH=/data/edix.db
      - EDIX_LOG_LEVEL=info
    restart: unless-stopped
    networks:
      - edix_network
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - edix
    networks:
      - edix_network

volumes:
  edix_data:

networks:
  edix_network:
    driver: bridge
```

# publish.sh - Script to publish to PyPI
```bash
#!/bin/bash

# Build and publish to PyPI

echo "Building Edix package..."

# Clean old builds
rm -rf build dist *.egg-info

# Build frontend first
cd frontend_src
npm install
npm run build
cd ..

# Build Python package
python -m build

# Check the build
echo "Checking distribution..."
twine check dist/*

# Upload to Test PyPI first (optional)
read -p "Upload to Test PyPI first? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    twine upload --repository testpypi dist/*
    echo "Test with: pip install --index-url https://test.pypi.org/simple/ edix"
    read -p "Continue to production PyPI? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

echo "✅ Published successfully!"
echo "Install with: pip install edix"
```

# Makefile
```makefile
.PHONY: help install dev build test lint format clean docker publish

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Install in development mode"
	@echo "  make build      - Build frontend and package"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make docker     - Build Docker image"
	@echo "  make publish    - Publish to PyPI"

install:
	pip install -e .

dev:
	pip install -e .[dev,export]
	cd frontend_src && npm install

build-frontend:
	cd frontend_src && npm run build

build: build-frontend
	python -m build

test:
	pytest tests/ -v --cov=edix

lint:
	ruff check edix/
	mypy edix/

format:
	black edix/
	ruff check --fix edix/

clean:
	rm -rf build dist *.egg-info
	rm -rf edix/__pycache__ edix/**/__pycache__
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf frontend_src/node_modules
	rm -rf edix/static/app.js

docker:
	docker build -t edix:latest .

docker-run:
	docker run -p 8000:8000 -v edix_data:/data edix:latest

publish: clean build
	twine check dist/*
	twine upload dist/*

serve:
	edix serve --reload

init-db:
	edix init
```

# .github/workflows/ci.yml - GitHub Actions CI/CD
```yaml
name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ created ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '20'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev,export]
        cd frontend_src && npm ci
    
    - name: Build frontend
      run: cd frontend_src && npm run build
    
    - name: Run tests
      run: pytest tests/ --cov=edix --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
    
    - name: Lint
      run: |
        ruff check edix/
        black --check edix/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*
```

# Example: Integracja z istniejącą aplikacją Flask/Django

## Flask Integration
```python
from flask import Flask, render_template
from edix import app as edix_app

flask_app = Flask(__name__)

# Mount Edix at /admin/editor
from werkzeug.middleware.dispatcher import DispatcherMiddleware
flask_app.wsgi_app = DispatcherMiddleware(
    flask_app.wsgi_app,
    {'/admin/editor': edix_app}
)

@flask_app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    flask_app.run()
```

## Django Integration
```python
# urls.py
from django.urls import path, re_path
from django.views.generic import TemplateView
import edix

urlpatterns = [
    # Your Django URLs
    path('', views.index, name='index'),
    
    # Mount Edix editor
    re_path(r'^editor/.*', edix.django_view),
]

# Or as middleware in settings.py
MIDDLEWARE = [
    # ... other middleware
    'edix.middleware.EdixMiddleware',
]
```

## JavaScript Widget Integration
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Application</title>
</head>
<body>
    <h1>My Application</h1>
    
    <!-- Embed Edix Editor -->
    <div id="edix-editor" 
         data-structure="products" 
         data-height="600">
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/edix-editor/dist/widget.js"></script>
    <script>
        EdixWidget.init({
            container: '#edix-editor',
            apiUrl: 'http://localhost:8000/api',
            structure: 'products',
            onSave: (data) => {
                console.log('Data saved:', data);
            }
        });
    </script>
</body>
</html>
```