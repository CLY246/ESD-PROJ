# import pika
# from os import environ

# # These module-level variables are initialized whenever a new instance of python interpreter imports the module;
# # In each instance of python interpreter (i.e., a program run), the same module is only imported once (guaranteed by the interpreter).
# hostname = environ.get('rabbit_host') or 'localhost'  # Default to 'localhost' if no environment variable is set
# port = environ.get('rabbit_port') or 5672  # Default to 5672 if no environment variable is set

# # Connect to the broker and set up a communication channel in the connection
# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(
#         host=hostname, port=port,
#         heartbeat=3600, blocked_connection_timeout=3600,  # These parameters to prolong the expiration time (in seconds) of the connection
#     )
# )

# channel = connection.channel()

# # Set up the exchange if the exchange doesn't exist
# exchangename = "order_topic"
# exchangetype = "topic"
# channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
# # 'durable' makes the exchange survive broker restarts

# # Declare and bind all needed queues
# def setup_queues():
#     # Error queue setup
#     queue_name = 'error'
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.error')

#     # Activity_log queue setup
#     queue_name = 'activity_log'
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='#')

#     # Order_notification queue setup
#     queue_name = 'order_notification'
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.order.notification')

# setup_queues()

# """
# This function in this module sets up a connection and a channel to a local AMQP broker,
# and declares a 'topic' exchange to be used by the microservices in the solution.
# """
# def check_setup():
#     global connection, channel, hostname, port, exchangename, exchangetype

#     if not is_connection_open(connection):
#         connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672, heartbeat=3600, blocked_connection_timeout=3600))
#         channel = connection.channel()
#         channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
#         setup_queues()  # Re-declare the queues if the connection is reset

# def is_connection_open(connection):
#     try:
#         connection.process_data_events()
#         return True
#     except pika.exceptions.AMQPError as e:
#         print("AMQP Error:", e)
#         print("...creating a new connection.")
#         return False

# # Ensure that the connection is closed when no longer needed
# def close_connection():
#     if connection and connection.is_open:
#         connection.close()

# if __name__ == "__main__":
#     try:
#         # Simulating the use of the connection
#         print("📡 RabbitMQ setup completed successfully.")
#     finally:
#         close_connection()  # Close the connection gracefully after usage


import pika
from os import environ
import time

# Default connection settings
hostname = environ.get('rabbit_host') or 'localhost'  # Default to 'localhost' if no environment variable is set
port = environ.get('rabbit_port') or 5672  # Default to 5672 if no environment variable is set

# Connection and channel setup
connection = None
channel = None
exchangename = "order_topic"
exchangetype = "topic"

def connect():
    """Establish a connection to RabbitMQ and return the connection and channel objects."""
    global connection, channel
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672, '/', pika.PlainCredentials('guest', 'guest')))
        channel = connection.channel()
        print("📡 Connection established successfully.")
        return connection, channel
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None, None

def setup_queues():
    """Declare and bind all needed queues."""
    global channel
    try:
        # Declare and bind the error queue
        queue_name = 'error'
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.error')

        # Declare and bind the activity_log queue
        queue_name = 'activity_log'
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='#')

        # Declare and bind the order_notification queue
        queue_name = 'order_notification'
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.order.notification')

        print("📦 Queues declared and bound successfully.")
    except pika.exceptions.AMQPError as e:
        print(f"AMQP Error during queue setup: {e}")

def is_connection_open():
    """Check if the connection is open and process events."""
    global connection
    if connection and connection.is_open:
        try:
            connection.process_data_events()  # This is necessary to keep the connection active
            return True
        except pika.exceptions.AMQPError as e:
            print(f"AMQP Error while checking connection status: {e}")
            return False
    return False

def check_setup():
    """Ensure the connection is open, and reconnect if needed."""
    global connection, channel
    if not is_connection_open():
        print("🔄 Re-establishing connection to RabbitMQ...")
        connection, channel = connect()
        if connection and channel:
            setup_queues()  # Re-declare the queues if the connection is reset
        else:
            print("Unable to reconnect to RabbitMQ, retrying...")
            time.sleep(5)  # Wait a few seconds before retrying
            check_setup()  # Recursively retry connection

def close_connection():
    """Ensure that the connection is closed when no longer needed."""
    global connection
    if connection and connection.is_open:
        connection.close()
        print("🔒 Connection closed.")

# Main entry point
if __name__ == "__main__":
    try:
        connection, channel = connect()  # Initial connection setup
        if connection and channel:
            setup_queues()  # Declare the queues after the connection is established
        else:
            print("Initial connection failed. Retrying...")
            check_setup()  # Retry connection if the initial one failed

        # Keep checking the connection periodically
        while True:
            check_setup()  # Ensure the connection stays active
            time.sleep(10)  # Check the connection every 10 seconds

    finally:
        close_connection()  # Gracefully close the connection when done
