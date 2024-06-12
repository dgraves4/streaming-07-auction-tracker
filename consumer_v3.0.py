"""
Real-Time Auction Tracker: Consumer Script with Util Logger and Rolling Window
This script reads bid messages from multiple RabbitMQ queues and maintains a rolling window of bids.

Author: Derek Graves
Date: June 11, 2024
Revised: June 12, 2024
"""

import pika
import json
import sys
from collections import deque
from util_logger import setup_logger

# Set up logger
logger, logname = setup_logger(__file__)

# Configuration for mapping queue names to item types
QUEUE_CONFIG = {
    'auction_queue_electronics': 'electronics',
    'auction_queue_furniture': 'furniture',
    'auction_queue_art': 'art'
}

# Rolling window configuration
ROLLING_WINDOWS = {
    'electronics': deque(maxlen=5),  # Track the last 5 bids for electronics
    'furniture': deque(maxlen=5),  # Track the last 5 bids for furniture
    'art': deque(maxlen=5)  # Track the last 5 bids for art
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
        logger.info(f"Received {item_type} message: {message['bid_amount']} at {message['timestamp']}")

        # Add message to the rolling window
        if item_type in ROLLING_WINDOWS:
            ROLLING_WINDOWS[item_type].append(message)
            # Log the summary of the rolling window
            latest_message = ROLLING_WINDOWS[item_type][-1]
            logger.info(f"Rolling window for {item_type} updated. Size: {len(ROLLING_WINDOWS[item_type])}, Latest bid: {latest_message['bid_amount']} at {latest_message['timestamp']}")

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
        
        # Declare queues and consume messages from each queue
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






