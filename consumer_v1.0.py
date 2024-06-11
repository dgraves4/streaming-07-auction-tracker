"""
Real-Time Auction Tracker: Basic Consumer Script
This script reads bid messages from a RabbitMQ queue and logs them.

Author: Derek Graves
Date: June 11, 2024
"""

import pika
import json
import logging
from util_logger import setup_logger

# Set up logger
logger, logname = setup_logger(__file__)

def callback(ch, method, properties, body):
    """
    Callback function for processing messages from the RabbitMQ queue.
    
    Parameters:
        ch: Channel object
        method: Method frame with delivery tag
        properties: Properties
        body: Message body (JSON string)
    """
    message = json.loads(body)
    logger.info(f"Received message: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """
    Main function to set up RabbitMQ consumer.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='auction_queue', durable=True)
        channel.basic_consume(queue='auction_queue', on_message_callback=callback)
        
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
