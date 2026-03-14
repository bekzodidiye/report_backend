# Production Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements/base.txt requirements/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/base.txt

# Copy project
COPY . .

# Add entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

# Default command to start the server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:10000", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120"]
