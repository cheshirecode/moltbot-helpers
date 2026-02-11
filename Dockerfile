FROM python:3.12-slim

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PT_DB_HOST=localhost \
    PT_DB_PORT=5433 \
    PT_DB_NAME=financial_analysis \
    PT_DB_USER=finance_user \
    PT_DB_PASSWORD=secure_finance_password

# Create non-root user for security with home directory
RUN groupadd -r moltbot && useradd -r -g moltbot -m -d /home/moltbot moltbot

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source files
COPY pyproject.toml ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install Python dependencies (without sentence-transformers - too heavy for Docker)
RUN pip install --no-cache-dir --break-system-packages \
    psycopg2-binary \
    flask \
    flask-cors \
    requests \
    numpy

# Install the package (makes pt, fp, seek available as CLI commands)
RUN pip install --no-cache-dir -e .

# Make scripts executable
RUN chmod +x scripts/*.py

# Create cache directory for any future needs
RUN mkdir -p /home/moltbot/.cache && chown -R moltbot:moltbot /home/moltbot

# Create startup script
RUN echo '#!/bin/bash\nset -e\nexec "$@"' > /app/startup.sh \
    && chmod +x /app/startup.sh

USER moltbot

ENTRYPOINT ["/app/startup.sh"]
CMD ["/bin/bash"]
