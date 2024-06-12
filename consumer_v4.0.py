"""
Real-Time Auction Tracker: Consumer Script with Util Logger, Rolling Window, and Email Alerts
This script reads bid messages from multiple RabbitMQ queues, maintains a rolling window of bids, and sends email alerts for high bids.

Author: Derek Graves
Date: June 11, 2024
Revised: June 12, 2024
"""

import pika
import json
import sys
from collections import deque
from util_logger import setup_logger
from emailer import createAndSendEmailAlert

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
    'electronics': deque(maxlen=5),
    'furniture': deque(maxlen=5),
    'art': deque(maxlen=5)
}

# Define the bid threshold
BID_THRESHOLD = 800  # Change this to an amount that will trigger alerts appropriately

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
        bid_amount = message['bid_amount']
        timestamp = message['timestamp']
        logger.info(f"Received {item_type} message: {bid_amount} at {timestamp}")

        # Add message to the rolling window
        if item_type in ROLLING_WINDOWS:
            ROLLING_WINDOWS[item_type].append(message)
            latest_message = ROLLING_WINDOWS[item_type][-1]
            logger.info(f"Rolling window for {item_type} updated. Size: {len(ROLLING_WINDOWS[item_type])}, Latest bid: {latest_message['bid_amount']} at {latest_message['timestamp']}")

            # Check if bid exceeds threshold
            if bid_amount > BID_THRESHOLD:
                logger.info(f"High bid alert: {bid_amount} at {timestamp}. Sending email alert.")
                subject = f"High Bid Alert: {item_type.capitalize()} - ${bid_amount}"
                body = f"A high bid of ${bid_amount} was placed on {item_type} at {timestamp}."
                createAndSendEmailAlert(subject, body)

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