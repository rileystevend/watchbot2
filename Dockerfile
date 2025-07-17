FROM python:3.11-slim
WORKDIR /app

# Install Chromium and matching ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app

CMD ["python", "watch_bot.py"]
