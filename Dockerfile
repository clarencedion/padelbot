# Use official Python slim image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libappindicator3-1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && dpkg -i chrome.deb || apt-get -fy install && \
    rm chrome.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.0/chromedriver/linux64/chromedriver.zip" \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver.zip

# Set environment variables for Chrome and ChromeDriver
ENV CHROME_BINARY="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"
ENV PATH="/usr/local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency file and install Python packages
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose the port (if needed)
EXPOSE 8000

# Command to run your application
CMD ["python", "app.py"]
