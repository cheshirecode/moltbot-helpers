# Use a Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DATA_DIR=/data \
    WORKSPACE_DIR=/workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Install additional dependencies for all tools
RUN pip install --no-cache-dir psutil watchdog

# Create default directories (will be overridden by volumes)
RUN mkdir -p ${DATA_DIR}/_openclaw \
    && mkdir -p ${WORKSPACE_DIR}/memory \
    && mkdir -p /root/.config/seek \
    && mkdir -p /app/config

# Copy and run the database initialization script
COPY init_databases.sh /app/init_databases.sh
RUN chmod +x /app/init_databases.sh

# Create default seek configuration that can be overridden
RUN echo '{"sources": ["${WORKSPACE_DIR}/memory", "${WORKSPACE_DIR}/MEMORY.md"]}' > /root/.config/seek/config.json

# Create default memory file if not provided
RUN echo "# MEMORY.md - OpenClaw Long-Term Memory\n\nThis is a placeholder for OpenClaw's long-term memory.\n\nLast updated: $(date +%Y-%m-%d %H:%M:%S)\n" > ${WORKSPACE_DIR}/MEMORY.md

# Create sample memory directory structure
RUN echo "# Daily Memory - $(date +%Y-%m-%d)\n\nToday's activities and notes.\n" > ${WORKSPACE_DIR}/memory/$(date +%Y-%m-%d).md

# Create default configuration for tools
RUN echo '{"default_project": "openclaw", "db_path": "${DATA_DIR}/_openclaw/project-tracker.db"}' > /app/config/pt_config.json

# Make the CLI tools available globally
RUN ln -sf /app/pt /usr/local/bin/pt && \
    ln -sf /app/fp /usr/local/bin/fp && \
    ln -sf /app/seek /usr/local/bin/seek && \
    ln -sf /app/integrate /usr/local/bin/integrate && \
    ln -sf /app/backup /usr/local/bin/backup && \
    ln -sf /app/service-manager /usr/local/bin/service-manager && \
    ln -sf /app/sync /usr/local/bin/sync && \
    ln -sf /app/lookup /usr/local/bin/lookup

# Create startup script to handle runtime configuration
RUN echo '#!/bin/bash\nset -e\n\n# Ensure data and workspace directories exist\nmkdir -p ${DATA_DIR}/_openclaw\nmkdir -p ${WORKSPACE_DIR}\n\n# Run command passed to container\nexec "$@"' > /app/startup.sh && \
    chmod +x /app/startup.sh

ENTRYPOINT ["/app/startup.sh"]
CMD ["/bin/bash"]