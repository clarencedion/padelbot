# Dockerfile
FROM python:3.10-slim

# Install system dependencies and libraries
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome version 100.0.4896.20
RUN wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_100.0.4896.20-1_amd64.deb" -O chrome.deb && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb

# Install ChromeDriver (ensure it matches the installed Chrome version)
# For example, if Chrome 133 is installed, we might use ChromeDriver 133.0.2789.41
RUN wget -q "https://chromedriver.storage.googleapis.com/100.0.4896.20/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Set a working directory
WORKDIR /app

# Copy dependency file and install Python packages
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . /app

# Expose the port your app runs on
EXPOSE 5000

# Command to run your application
CMD ["python", "app.py"]
