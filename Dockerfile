    
ARG PYTHON_VERSION=3.14.3
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install package manager 
RUN pipx install uv

# Install dependencies
RUN uv sync

# Copy directory
Copy . .

# Expose Port
EXPOSE 8888


#  Run command 
CMD ["uv","run","fastapi","run","--port","8888"]


