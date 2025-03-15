# Use official Python image as a base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the service files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask application port
EXPOSE 5100

# Run the AMQP setup and then start the Flask service
CMD ["sh", "-c", "python rabbitmq/amqp_setup.py && python place_an_order.py"]
