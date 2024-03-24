# Start from a slim version of Python 3.10
FROM python:3.10-slim

# Set Python Envs
ENV HOME=/opt APP_HOME=/opt PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR $APP_HOME

# Copy Python dependencies
COPY ../requirements.txt .

# Install in a single layer, and clean up in the same layer to minimize image size
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
    && pip install --prefer-binary --no-cache-dir --upgrade pip \
    && pip install --prefer-binary --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY ../src ./src

# Run app - exec form (doesn’t start a shell on its own)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
