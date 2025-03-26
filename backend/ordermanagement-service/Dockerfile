# FROM python:3-slim
# WORKDIR /app
# COPY . .
# COPY requirements.txt .
# RUN python -m pip install --no-cache-dir -r requirements.txt
# EXPOSE 5000
# CMD ["python", "ordermanagement.py"]




# Use official Python image as a base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the service files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose the Flask application port
EXPOSE 5000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
