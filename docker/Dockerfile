###########
# BUILDER #
###########
FROM python:3.9 AS builder

WORKDIR /opt
COPY ../requirements.txt .

# Install build dependencies and Python dependencies
RUN apt-get update && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install -r requirements.txt


#########
# FINAL #
#########
FROM python:3.9-slim

# Set Python Envs
ENV HOME=/opt
ENV APP_HOME=/opt
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy Python dependencies and binaries
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Install runtime dependencies and creates user
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy app code
WORKDIR $APP_HOME
COPY ../src ./src
COPY ../.env .

# Run app - exec form (doesn’t start a shell on its own)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
