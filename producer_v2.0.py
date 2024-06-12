"""
Real-Time Auction Tracker: Producer Script with Faker and Logging
This script sends synthetic bid messages to a RabbitMQ queue.

Author: Derek Graves
Date: January 15, 2023
Revised: June 11, 2024
"""

import pika
import sys
import webbrowser
import json
from faker import Faker
import logging
import random  
from util_logger import setup_logger
from datetime import datetime  

# Set up logger
logger, logname = setup_logger(__file__)

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? (y/n): ")
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info("Opened RabbitMQ Admin site.")

def send_message(host: str, queue_name: str, message: dict):
    """
    Sends a message to the specified RabbitMQ queue.
    
    Parameters:
        host (str): RabbitMQ server hostname or IP address
        queue_name (str): Name of the queue
        message (dict): Message to be sent
    """
    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
        logger.info(f"Sent message: {message}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
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
        'bid_amount': round(random.uniform(10, 1000), 2),
        'timestamp': datetime.utcnow().isoformat(),
        'item': fake.word(),
        'bidder_name': fake.name(),
        'bidder_email': fake.email()
    }
    logger.debug(f"Generated fake bid: {bid}")
    return bid

if __name__ == "__main__":
    offer_rabbitmq_admin_site()
    fake = Faker()
    message = generate_fake_bid(fake)
    send_message("localhost", "auction_queue", message)
