# Start from a slim version of Python 3.12
FROM python:3.12-slim

# Set Python Envs
ENV HOME=/opt APP_HOME=/opt PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR $APP_HOME

# Copy Python dependencies and the local CRUD library
# (installed from source until fastapi-crud-base is published to PyPI)
COPY requirements.txt .
COPY libs/fastapi-crud-base ./libs/fastapi-crud-base

# Install in a single layer, and clean up in the same layer to minimize image size
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
    && pip install --prefer-binary --no-cache-dir --upgrade pip \
    && pip install --prefer-binary --no-cache-dir -r requirements.txt \
    && pip install --prefer-binary --no-cache-dir --no-deps ./libs/fastapi-crud-base \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY src ./src

# Run app - exec form (doesn't start a shell on its own)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
