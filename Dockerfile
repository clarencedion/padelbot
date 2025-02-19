# Dockerfile
FROM python:3.10-slim

# Install dependencies for Chrome and fonts
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Install latest ChromeDriver
RUN LATEST=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE") && \
    wget -q "https://chromedriver.storage.googleapis.com/${LATEST}/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Set display port for headless Chrome
ENV DISPLAY=:99

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]
