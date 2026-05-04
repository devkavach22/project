ARG PYTHON_VERSION=3.14.3
FROM python:${PYTHON_VERSION}-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (optional but recommended)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (IMPORTANT: done at build time)
RUN uv sync --frozen

# Copy rest of the code
COPY . .

# Expose port
EXPOSE 8888

# Run app
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8888"]


