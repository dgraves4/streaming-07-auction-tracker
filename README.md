# streaming-07-auction-tracker
This project is a real-time auction tracking system using RabbitMQ to stream, process, and analyze bid data. This project generates synthetic bid messages and processes them to simulate a live auction environment using custom producer and consumer scripts.

## Repository Structure
- producer_v1.0.py: Generates and sends synthetic bid messages.
- consumer_v1.0.py: Reads and logs messages from the queue.
- util_logger.py: Sets up logging for the project.
- README.md: Project documentation (this file).

## Project Goals 
- Stream live bid data: Handle bid data in-real time.
- Simulate Bidding: Use synthetic data to mimic an auction scenario.
- Implement RabbitMQ: Use RabbitMQ for message queuing.
- Logging and Monitoring: Use loggin instead of print statements for additional visibility and debugging.

## Data Sources
- Faker Library: Generates realistic auction data including bidder details and bid amounts.
- Custom Data Handling: Simulate both good and bad data to demonstrate error handling. 

## Dependencies
- Python
- pika: For RabbitMQ integration
- faker: Generates synthetic data 
- logging: Python's logger module
- json: Handling JSON data
- random: Generates random values
- datetime: Handles dates and times

## Project Setup

1. Prerequisites
- Python: Ensure you have Python 3.10 or later installed.
- RabbitMQ: Ensure RabbitMQ is installed and running on localhost. Visit http://localhost:15672 for the RabbitMQ admin interface.

2. Clone the Repository 
- Start a new repository and copy the files, or clone the repository to your local machine: 
```bash
git clone https://github.com/your-username/streaming-07-auction-tracker.git
cd streaming-07-auction-tracker
```
3. Setting up Virtual Environment
- Create virtual environment: 
```bash
python -m venv .venv
```
- Activate the virtual environment:
```bash
source .venv/scripts/activate
```
4. With the virtual environment activated, install the necessary dependencies:

```bash
pip install pika faker
```
- Generate requirements.txt for dependency tracking:
```bash
pip freeze > requirements.txt
```

5.  Update .gitignore file with environment to leave it out of version control:
```bash
echo ".venv/" >> .gitignore
```
or simply add .venv into the .gitignore file. 

## Running the Project
Step-by-Step Execution Guide

1. Run Producer
In your terminal, ensure you are in the project directory and the virtual environment is activated. Then, run the producer script:

```bash
python producer_v1.0.py
```

Expected Output from Console:

```bash
Would you like to monitor RabbitMQ queues? (y/n): y
Opened RabbitMQ Admin site.
Sent message: {'bidder_id': '...', 'bid_amount': ..., 'timestamp': '...', 'item': '...', 'bidder_name': '...', 'bidder_email': '...'}
Closed RabbitMQ connection
```
A log file will also be generated with the message details in logs/producer_v1.0.log.

2. Run Consumer
In a separate terminal, navigate to the project directory, activate the virtual environment, and run the consumer script:

```bash
python consumer_v1.0.py
```

Expected Output from Console:

```bash
Starting consumer. Waiting for messages...
Received message: {'bidder_id': '...', 'bid_amount': ..., 'timestamp': '...', 'item': '...', 'bidder_name': '...', 'bidder_email': '...'}
```
A log file will also be generated when running the consumer in 'logs/consumer_v1.0.log'.

### Simulated Run

Follow these steps to simulate a complete run:

1. Start RabbitMQ: Ensure RabbitMQ server is running.
2. Run Producer: Open a terminal and execute python producer_v1.0.py. This will generate and send a synthetic bid message.
3. Run Consumer: Open another terminal and execute python consumer_v1.0.py. This will read and log the message sent by the producer.
4. Verify the queue status in the RabbitMQ admin interface and check logs for both producer and consumer to confirm successful message handling.

## Screenshots

1. RabbitMQ Admin Interface: 

2. Console Outputs:

## Sources 
