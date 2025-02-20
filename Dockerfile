# Use official Python slim image
FROM python:3.10-slim

# Install system dependencies and required libraries
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
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
    && rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome 133.0.6943.126
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chrome-linux64.zip" -O chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /opt/ && \
    rm chrome-linux64.zip && \
    mv /opt/chrome-linux64 /opt/chrome && \
    ln -s /opt/chrome/chrome /usr/bin/google-chrome

# Download and install ChromeDriver 133.0.6943.126
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip" -O chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /opt/ && \
    rm chromedriver-linux64.zip && \
    mv /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver

# Set environment variables for Selenium
ENV DISPLAY=:99
ENV CHROME_BINARY="/usr/bin/google-chrome"

# Set a working directory
WORKDIR /app

# Copy dependency file and install Python packages
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . /app

# Expose the correct port
EXPOSE 8000

# Set the environment variable for Flask to use port 8000
ENV PORT=8000

# Command to run your application
CMD ["python", "app.py"]
