FROM python:3.11-slim
WORKDIR /app

# Install dependencies via pip
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . /app

# Default command
CMD ["python", "watch_bot.py"]
