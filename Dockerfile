# Use official Python slim image
FROM python:3.10-slim

# Install dependencies required for Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    jq \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libcurl4 \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Step 1: Fetch the latest ChromeDriver version
RUN LATEST_DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | jq -r '.channels.Stable.version') && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${LATEST_DRIVER_VERSION}/chromedriver/linux64/chromedriver.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Step 2: Install Google Chrome that matches the latest ChromeDriver version
RUN LATEST_CHROME_VERSION=$(chromedriver --version | awk '{print $2}') && \
    wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${LATEST_CHROME_VERSION}-1_amd64.deb" -O /tmp/google-chrome.deb && \
    dpkg -i /tmp/google-chrome.deb || apt-get install -fy && \
    rm /tmp/google-chrome.deb

# Verify Chrome installation
RUN which google-chrome
RUN google-chrome --version

# Verify ChromeDriver installation
RUN which chromedriver
RUN chromedriver --version

# Set environment variables
ENV CHROME_BINARY="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"
ENV PATH="/usr/local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
