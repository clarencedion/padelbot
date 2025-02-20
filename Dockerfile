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

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
      >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (ensure it matches the installed Chrome version)
# For example, if Chrome 133 is installed, we might use ChromeDriver 133.0.2789.41
RUN wget -q "https://chromedriver.storage.googleapis.com/133.0.2789.41/chromedriver_linux64.zip" && \
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
