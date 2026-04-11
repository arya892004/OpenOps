# Simple Dockerfile using pip instead of uv
FROM python:3.11-slim

WORKDIR /app/env

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . /app/env

# Install Python dependencies
RUN pip install --no-cache-dir \
    openenv-core>=0.2.2 \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    pydantic>=2.0.0 \
    openai>=1.0.0

# Set Python path
ENV PYTHONPATH="/app/env:$PYTHONPATH"

# Expose port
EXPOSE 7860

# Start server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]