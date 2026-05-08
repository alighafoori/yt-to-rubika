FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies AND clean up in the SAME layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Install Bun and clean up in the SAME layer
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun && \
    rm -rf /root/.bun/.cache /root/.bun/install-cache

# Make sure local Python binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy only necessary files
COPY app.py .
COPY d.sh .
COPY d-direct.sh .
COPY r1.py .
COPY templates/ ./templates/

RUN chmod +x d.sh d-direct.sh && \
    mkdir -p /app/data

EXPOSE 5000

CMD ["python", "-u", "app.py"]