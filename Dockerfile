# syntax=docker/dockerfile:1-labs

FROM python:3.13-slim

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY ./app /app

# Install dependencies using uv with --system flag for Docker environments
RUN uv pip install --system --no-cache -e .

WORKDIR /app
# Expose the application port
EXPOSE 8000
# Run the application
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8000"]