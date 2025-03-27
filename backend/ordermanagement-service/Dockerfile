# FROM python:3-slim
# WORKDIR /app
# COPY . .
# COPY requirements.txt .
# RUN python -m pip install --no-cache-dir -r requirements.txt
# EXPOSE 5000
# CMD ["python", "ordermanagement.py"]




# Use official Python image as a base
FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
