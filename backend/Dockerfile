# Multi-stage build for optimized image size

FROM python:3.11-alpine AS builder

# Install build dependencies

RUN apk add –no-cache gcc musl-dev postgresql-dev

# Set working directory

WORKDIR /app

# Copy requirements and install dependencies

COPY requirements.txt .
RUN pip install –no-cache-dir –user -r requirements.txt

# Final stage

FROM python:3.11-alpine

# Install runtime dependencies only

RUN apk add –no-cache libpq curl &&   
addgroup -g 1000 appuser &&   
adduser -D -u 1000 -G appuser appuser

# Set working directory

WORKDIR /app

# Copy Python dependencies from builder

COPY –from=builder /root/.local /home/appuser/.local

# Copy application code

COPY –chown=appuser:appuser app.py config.py ./

# Update PATH

ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user

USER appuser

# Expose port

EXPOSE 5000

# Health check

HEALTHCHECK –interval=30s –timeout=3s –start-period=5s –retries=3   
CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application

CMD [“python”, “app.py”]
