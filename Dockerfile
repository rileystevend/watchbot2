FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc build-essential wget \
    && pip install --upgrade pip \
    && pip install -r requirements.txt
COPY . /app
CMD ["python", "watch_bot.py"]
