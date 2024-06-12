"""
Real-Time Auction Tracker: Enhanced Consumer Script
This script reads bid messages from multiple RabbitMQ queues and logs them.

Author: Derek Graves
Date: June 11, 2024
"""

import pika
import json
import sys
from util_logger import setup_logger

# Set up logger
logger, logname = setup_logger(__file__)

# Configuration for mapping queue names to item types
QUEUE_CONFIG = {
    'auction_queue_electronics': 'electronics',
    'auction_queue_furniture': 'furniture',
    'auction_queue_art': 'art'
}

def callback(ch, method, properties, body):
    """
    Callback function for processing messages from the RabbitMQ queue.
    
    Parameters:
        ch: Channel object
        method: Method frame containing delivery tag
        properties: Properties of the message
        body: The actual message body (JSON string)
    """
    try:
        message = json.loads(body)  # Decode the JSON message
        item_type = QUEUE_CONFIG.get(method.routing_key, 'unknown')  # Get item type based on queue
        logger.info(f"Received {item_type} message: {message}")
        # You can perform additional processing or analytics here
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Reject the message without requeueing
    except Exception as e:
        logger.error(f"An error occurred while processing the message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Reject the message without requeueing

def main():
    """
    Main function to set up RabbitMQ consumer.
    """
    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        # Declare and consume messages from each queue
        for queue_name in QUEUE_CONFIG.keys():
            channel.queue_declare(queue=queue_name, durable=True)  # Declare the queue as durable
            channel.basic_consume(queue=queue_name, on_message_callback=callback)  # Set callback for the queue
        
        logger.info("Starting consumer. Waiting for messages...")
        channel.start_consuming()  # Start consuming messages
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection to RabbitMQ server failed: {e}")
        sys.exit(1)  # Exit if connection fails
    except KeyboardInterrupt:
        logger.info("Consumer interrupted. Closing connection.")
        if 'connection' in locals() and connection.is_open:
            connection.close()  # Close the connection gracefully

if __name__ == "__main__":
    main()  # Run the main function if this script is executed directly



