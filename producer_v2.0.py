"""
Real-Time Auction Tracker: Enhanced Producer Script
This script sends synthetic bid messages to multiple RabbitMQ queues.

Author: Derek Graves
Date: June 11, 2024
"""

import pika
import sys
import webbrowser
import json
from faker import Faker
import random  
from util_logger import setup_logger
from datetime import datetime, timezone  

# Set up logger
logger, logname = setup_logger(__file__)

# Configuration mapping for queues based on item types
QUEUE_CONFIG = {
    'electronics': 'auction_queue_electronics',
    'furniture': 'auction_queue_furniture',
    'art': 'auction_queue_art'
}

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website for monitoring queues."""
    ans = input("Would you like to monitor RabbitMQ queues? (y/n): ")
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info("Opened RabbitMQ Admin site.")

def send_message(host: str, queue_name: str, message: dict):
    """
    Sends a message to the specified RabbitMQ queue.
    
    Parameters:
        host (str): RabbitMQ server hostname or IP address
        queue_name (str): Name of the queue to send the message to
        message (dict): The message data to be sent
    """
    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        # Open a communication channel using the connection
        channel = connection.channel()
        # Declare a durable queue to ensure it survives RabbitMQ restarts
        channel.queue_declare(queue=queue_name, durable=True)
        # Publish the message to the specified queue
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),  # Convert message dictionary to JSON string
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        logger.info(f"Sent message: {message}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection to RabbitMQ server failed: {e}")
        sys.exit(1)  # Exit if connection fails
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        # Ensure the connection is closed
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Closed RabbitMQ connection.")

def generate_fake_bid(fake):
    """
    Generates a fake bid using the Faker library.
    
    Parameters:
        fake (Faker): An instance of the Faker class.
    
    Returns:
        dict: A dictionary representing a fake bid.
    """
    bid = {
        'bidder_id': fake.uuid4(),
        'bid_amount': round(random.uniform(10, 1000), 2),  # Random bid amount between $10 and $1000
        'timestamp': datetime.now(timezone.utc).isoformat(),  # Current time in ISO format
        'item': fake.random_element(elements=('electronics', 'furniture', 'art')),  # Random item type
        'bidder_name': fake.name(),
        'bidder_email': fake.email()
    }
    logger.debug(f"Generated fake bid: {bid}")
    return bid

if __name__ == "__main__":
    offer_rabbitmq_admin_site()  # Optionally open RabbitMQ admin site
    fake = Faker()  # Initialize Faker for generating fake data
    message = generate_fake_bid(fake)  # Generate a fake bid
    
    # Determine queue based on item type
    item_type = message['item']
    queue_name = QUEUE_CONFIG.get(item_type, 'auction_queue_default')  # Default queue if item type not found
    
    send_message("localhost", queue_name, message)  # Send the message to the appropriate queue


