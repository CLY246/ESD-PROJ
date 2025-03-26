FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install tensorflow pandas numpy flask psycopg2-binary requests flask-cors
EXPOSE 5000
CMD ["python", "recommendation.py"]






