FROM python:3.10-slim
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
COPY . .
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
    
EXPOSE 5000
CMD ["python", "recommendation.py"]






