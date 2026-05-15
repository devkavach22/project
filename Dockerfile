ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

# -----------------------------
# Python settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    poppler-utils \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install uv
# -----------------------------
RUN pip install --no-cache-dir uv

# -----------------------------
# Copy dependency files
# -----------------------------
COPY pyproject.toml uv.lock ./

# -----------------------------
# Install Python dependencies
# -----------------------------
RUN uv sync --frozen

# -----------------------------
# Copy app
# -----------------------------
COPY . .

# -----------------------------
# Expose FastAPI port
# -----------------------------
EXPOSE 8888

# -----------------------------
# Start app
# -----------------------------
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8888"]