FROM python:3-slim
WORKDIR /app
COPY . .
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

