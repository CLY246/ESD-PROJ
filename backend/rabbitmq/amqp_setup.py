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


# import pika
# from os import environ

# # Default connection settings
# hostname = environ.get('rabbit_host', 'rabbitmq')
# port = int(environ.get('rabbit_port', 5673))  # Explicitly convert to integer

# def create_connection():
#     return pika.BlockingConnection(
#         pika.ConnectionParameters(
#             host=hostname, port=port,
#             heartbeat=3600, blocked_connection_timeout=3600
#         )
#     )

# # Establish connection
# try:
#     connection = create_connection()
#     channel = connection.channel()
# except pika.exceptions.AMQPConnectionError as e:
#     print(f"Failed to connect to RabbitMQ: {e}")
#     exit(1)

# # Set up the exchange
# exchangename = "order_topic"
# exchangetype = "topic"
# channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

# # Declare and bind all needed queues
# def setup_queues():
#     try:
#         # Error queue setup
#         channel.queue_declare(queue='error', durable=True)
#         channel.queue_bind(exchange=exchangename, queue='error', routing_key='*.error')

#         # Activity_log queue setup
#         channel.queue_declare(queue='activity_log', durable=True)
#         channel.queue_bind(exchange=exchangename, queue='activity_log', routing_key='#')

#         # Order_notification queue setup
#         channel.queue_declare(queue='order_notification', durable=True)
#         channel.queue_bind(exchange=exchangename, queue='order_notification', routing_key='*.order.notification')

#     except pika.exceptions.AMQPError as e:
#         print(f"Queue setup failed: {e}")

# setup_queues()

# # Check and restore connection if needed
# def check_setup():
#     global connection, channel
#     if not is_connection_open(connection):
#         print("Re-establishing connection...")
#         connection = create_connection()
#         channel = connection.channel()
#         channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
#         setup_queues()  # Ensure queues are re-declared

# def is_connection_open(conn):
#     try:
#         conn.process_data_events()
#         return True
#     except pika.exceptions.AMQPError:
#         return False







import pika
import time
from os import environ

# Default connection settings
hostname = environ.get('rabbit_host', 'rabbitmq')
port = int(environ.get('rabbit_port', 5672))  # Explicitly convert to integer

# Exchange constants
EXCHANGE_NAME = "order_topic"
EXCHANGE_TYPE = "topic"

def create_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname, port=port,
            heartbeat=3600,
            blocked_connection_timeout=3600
        )
    )

def create_connection_with_retry(retries=10, delay=5):
    for attempt in range(1, retries + 1):
        try:
            print(f"Trying to connect to RabbitMQ at {hostname}:{port} (attempt {attempt}/{retries})")
            connection = create_connection()
            print("Connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}")
            if attempt < retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Exceeded maximum retries. Exiting.")
                exit(1)



def setup_queues_with_channel(channel):
    try:
        # Error queue
        channel.queue_declare(queue='error', durable=True)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue='error', routing_key='*.error')

        # Activity log queue
        channel.queue_declare(queue='activity_log', durable=True)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue='activity_log', routing_key='#')

        # Order notification queue
        channel.queue_declare(queue='order_notification', durable=True)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue='order_notification', routing_key='#.order.notification')

        print("Queues set up successfully.")
    except pika.exceptions.AMQPError as e:
        print(f"Queue setup failed: {e}")

def connect():
    """Establish connection and channel, declare exchange and queues, return both."""
    connection = create_connection_with_retry()
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
    setup_queues_with_channel(channel)
    return connection, channel

def is_connection_open(conn):
    try:
        conn.process_data_events()
        return True
    except pika.exceptions.AMQPError:
        return False

def check_setup(connection, channel):
    """Optional helper for restoring connection."""
    if not is_connection_open(connection):
        print("🔁 Re-establishing RabbitMQ connection...")
        return connect()
    return connection, channel
