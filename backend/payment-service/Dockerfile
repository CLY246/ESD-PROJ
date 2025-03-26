FROM python:3-slim
WORKDIR /app
COPY . .
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


EXPOSE 5000
CMD ["python", "payment.py"]
