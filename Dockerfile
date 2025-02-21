# Use official Python slim image
FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Install dependencies required for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    xdg-utils \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libcups2 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome using Google's official package (alternative approach)
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo 'deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Verify Chrome installation
RUN google-chrome --version || echo "Google Chrome failed to install"

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.0/chromedriver/linux64/chromedriver.zip" \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver.zip

# Set environment variables
ENV CHROME_BINARY="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"
ENV PATH="/usr/local/bin:/usr/bin:/bin:${PATH}"

# Copy project dependencies and install Python packages
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose the correct port
EXPOSE 8000

# Start the application
CMD ["python", "app.py"]
