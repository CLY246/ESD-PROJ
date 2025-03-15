# #!/usr/bin/env python3

# """
# AMQP Setup: Creates exchanges and queues on RabbitMQ.
# """

# import pika
# import sys

# # RabbitMQ Connection Parameters
# RABBIT_HOST = "rabbitmq"  # Use the service name in docker-compose
# RABBIT_PORT = 5672
# EXCHANGE_NAME = "order_topic"
# EXCHANGE_TYPE = "topic"

# # Define queues and routing keys
# QUEUES = {
#     "Error": "*.error",
#     "Activity_Log": "#",
#     "Notification": "order.notification",
# }


# def create_exchange_and_queues():
#     """
#     Connect to RabbitMQ, declare exchange and queues, then bind them with routing keys.
#     """
#     try:
#         print(f"📡 Connecting to RabbitMQ at {RABBIT_HOST}:{RABBIT_PORT}...")
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=RABBIT_HOST,
#                 port=RABBIT_PORT,
#                 heartbeat=300,
#                 blocked_connection_timeout=300,
#             )
#         )
#         channel = connection.channel()

#         # Declare Exchange
#         print(f"🔄 Declaring Exchange: {EXCHANGE_NAME} ({EXCHANGE_TYPE})")
#         channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)

#         # Declare and bind queues
#         for queue_name, routing_key in QUEUES.items():
#             print(f"✅ Declaring Queue: {queue_name} (Routing Key: {routing_key})")
#             channel.queue_declare(queue=queue_name, durable=True)
#             channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key)

#         print("🎉 AMQP Setup Complete! RabbitMQ is ready.")
#         connection.close()

#     except Exception as e:
#         print(f"❌ Error setting up RabbitMQ: {e}")
#         sys.exit(1)


# if __name__ == "__main__":
#     create_exchange_and_queues()





import pika
import sys

# RabbitMQ Connection Parameters
RABBIT_HOST = "rabbitmq"  # Service name in docker-compose
RABBIT_PORT = 5672
EXCHANGE_NAME = "order_topic"
EXCHANGE_TYPE = "topic"

# Define queues and routing keys
QUEUES = {
    "Error": "*.error",
    "Activity_Log": "#",
    "Notification": "order.notification",
}

def connect():
    """
    Connect to RabbitMQ and return the channel.
    """
    try:
        print(f"📡 Connecting to RabbitMQ at {RABBIT_HOST}:{RABBIT_PORT}...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBIT_HOST,
                port=RABBIT_PORT,
                heartbeat=300,
                blocked_connection_timeout=300,
            )
        )
        channel = connection.channel()

        print(f"🔄 Declaring Exchange: {EXCHANGE_NAME} ({EXCHANGE_TYPE})")
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)

        # Declare and bind queues
        for queue_name, routing_key in QUEUES.items():
            print(f"✅ Declaring Queue: {queue_name} (Routing Key: {routing_key})")
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key)

        print("🎉 AMQP Setup Complete! RabbitMQ is ready.")
        return connection, channel  # Return the connection and channel

    except Exception as e:
        print(f"❌ Error setting up RabbitMQ: {e}")
        sys.exit(1)


if __name__ == "__main__":
    connect()
