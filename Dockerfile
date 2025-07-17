FROM python:3.11-slim
WORKDIR /app

# Install Chrome browser and driver dependencies
RUN apt-get update && apt-get install -y chromium chromium-driver \
    && pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . /app

# Default command
CMD ["python", "watch_bot.py"]

