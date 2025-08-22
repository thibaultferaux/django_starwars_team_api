# Build stage
FROM python:3.13-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# Production stage
FROM python:3.13-slim AS production

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install only the necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels directory from the builder stage
COPY --from=builder /wheels /wheels

# Copy requirements.txt from the builder stage
COPY requirements.txt .

# Install packages from wheels
RUN pip install --no-cache-dir --find-links /wheels -r requirements.txt

# Use a non-root user for security
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

# Copy application code
COPY . .

# Expose port 8000 to allow external access
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]





