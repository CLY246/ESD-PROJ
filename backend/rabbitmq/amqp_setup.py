import pika
from os import environ

# These module-level variables are initialized whenever a new instance of python interpreter imports the module;
# In each instance of python interpreter (i.e., a program run), the same module is only imported once (guaranteed by the interpreter).
hostname = environ.get('rabbit_host') or 'localhost'  # Default to 'localhost' if no environment variable is set
port = environ.get('rabbit_port') or 5672  # Default to 5672 if no environment variable is set

# Connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600,  # These parameters to prolong the expiration time (in seconds) of the connection
    )
)

channel = connection.channel()

# Set up the exchange if the exchange doesn't exist
exchangename = "order_topic"
exchangetype = "topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
# 'durable' makes the exchange survive broker restarts

# Declare and bind all needed queues
def setup_queues():
    # Error queue setup
    queue_name = 'error'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.error')

    # Activity_log queue setup
    queue_name = 'activity_log'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='#')

    # Order_notification queue setup
    queue_name = 'order_notification'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.order.notification')

setup_queues()

"""
This function in this module sets up a connection and a channel to a local AMQP broker,
and declares a 'topic' exchange to be used by the microservices in the solution.
"""
def check_setup():
    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
        setup_queues()  # Re-declare the queues if the connection is reset

def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False

# Ensure that the connection is closed when no longer needed
def close_connection():
    if connection and connection.is_open:
        connection.close()

if __name__ == "__main__":
    try:
        # Simulating the use of the connection
        print("📡 RabbitMQ setup completed successfully.")
    finally:
        close_connection()  # Close the connection gracefully after usage
