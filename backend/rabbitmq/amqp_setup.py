

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
        # channel.queue_bind(exchange=EXCHANGE_NAME, queue='order_notification', routing_key='#.order.notification')
        channel.queue_bind(exchange=EXCHANGE_NAME, queue='order_notification', routing_key='order.placed.order.notification')
        channel.queue_bind(exchange=EXCHANGE_NAME, queue='order_notification', routing_key='order.placed.grouporder.notification') 


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
