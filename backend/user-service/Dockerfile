FROM python:3-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=user.py
ENV FLASK_ENV=development
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "user:app"]
