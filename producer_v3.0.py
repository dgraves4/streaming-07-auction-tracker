"""
Real-Time Auction Tracker: Continuous Producer Script with Util Logger
This script continuously sends synthetic bid messages to multiple RabbitMQ queues with an open connection.

Author: Derek Graves
Date: January 15, 2023
Revised: June 12, 2024
"""

import pika
import json
from faker import Faker
import random
from datetime import datetime, timezone
import time
import webbrowser  # Import for opening the web browser
from util_logger import setup_logger

# Set up logger
logger, logname = setup_logger(__file__)

# Configuration mapping for queues based on item types
QUEUE_CONFIG = {
    'electronics': 'auction_queue_electronics',
    'furniture': 'auction_queue_furniture',
    'art': 'auction_queue_art'
}

# Time interval (in seconds) between sending messages
MESSAGE_INTERVAL = 5

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website for monitoring queues."""
    ans = input("Would you like to monitor RabbitMQ queues? (y/n): ")
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info("Opened RabbitMQ Admin site.")

def send_message(channel, queue_name: str, message: dict):
    """
    Sends a message to the specified RabbitMQ queue.
    
    Parameters:
        channel: The channel object for sending messages
        queue_name (str): Name of the queue to send the message to
        message (dict): The message data to be sent
    """
    # Declare a durable queue and publish the message
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),  # Convert message dictionary to JSON string
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )
    logger.info(f"Sent message to {queue_name}: Bid Amount: {message['bid_amount']} at {message['timestamp']}")

def generate_fake_bid(fake):
    """
    Generates a fake bid using the Faker library.
    
    Parameters:
        fake (Faker): An instance of the Faker class.
    
    Returns:
        dict: A dictionary representing a fake bid.
    """
    return {
        'bidder_id': fake.uuid4(),
        'bid_amount': round(random.uniform(10, 1000), 2),  # Random bid amount between $10 and $1000
        'timestamp': datetime.now(timezone.utc).isoformat(),  # Current time in ISO format
        'item': fake.random_element(elements=('electronics', 'furniture', 'art')),  # Random item type
        'bidder_name': fake.name(),
        'bidder_email': fake.email()
    }

if __name__ == "__main__":
    offer_rabbitmq_admin_site()  # Optionally open RabbitMQ admin site
    fake = Faker()  # Initialize Faker for generating fake data

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        logger.info("Producer started. Sending messages to RabbitMQ queues.")
        
        while True:
            message = generate_fake_bid(fake)  # Generate a fake bid
            # Determine queue based on item type
            item_type = message['item']
            queue_name = QUEUE_CONFIG.get(item_type, 'auction_queue_default')  # Default queue if item type not found
            send_message(channel, queue_name, message)  # Send the message to the appropriate queue
            time.sleep(MESSAGE_INTERVAL)  # Wait before sending the next message

    except KeyboardInterrupt:
        logger.info("Producer interrupted. Exiting.")
    finally:
        if channel.is_open:
            channel.close()  # Close the channel
            logger.info("Closed RabbitMQ channel.")
        if connection.is_open:
            connection.close()  # Close the connection
            logger.info("Closed RabbitMQ connection.")





