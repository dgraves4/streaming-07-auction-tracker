"""
Real-Time Auction Tracker: Enhanced Consumer Script
This script reads bid messages from multiple RabbitMQ queues and logs them.

Author: Derek Graves
Date: June 11, 2024
"""

import pika
import json
import logging
import sys
from util_logger import setup_logger

# Set up logger
logger, logname = setup_logger(__file__)

# Define queues for different auction items
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
        method: Method frame with delivery tag
        properties: Properties
        body: Message body (JSON string)
    """
    try:
        message = json.loads(body)
        item_type = QUEUE_CONFIG.get(method.routing_key, 'unknown')
        logger.info(f"Received {item_type} message: {message}")
        # Perform simple operations or analytics here if needed
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"An error occurred while processing the message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    """
    Main function to set up RabbitMQ consumer.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        for queue_name in QUEUE_CONFIG.keys():
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_consume(queue=queue_name, on_message_callback=callback)
        
        logger.info("Starting consumer. Waiting for messages...")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Consumer interrupted. Closing connection.")
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == "__main__":
    main()

