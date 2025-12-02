# Use Python 3.10 slim image
FROM python:3.10-slim

# Install system dependencies for Chromium browser (required for Playwright/Crawl4AI)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (required for Crawl4AI to work)
RUN python -m playwright install chromium

# Copy the application code
COPY . .

# Create output directory for agent results
RUN mkdir -p ai-agent-output

# Make the startup script executable
RUN chmod +x start.sh

# Expose Streamlit port
EXPOSE 8501

# Set the startup script as entrypoint
CMD ["./start.sh"]
