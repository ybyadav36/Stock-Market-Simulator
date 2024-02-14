import os
from confluent_kafka import Consumer, KafkaException
import logging
import yaml
from confluent_kafka.cimpl import KafkaError

# Get the path to the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration from config.yml in the root directory
config_file_path = os.path.join(root_dir, "config.yml")
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Kafka consumer configuration
kafka_consumer_config = {
    'bootstrap.servers': config['development']['kafka']['bootstrap_servers'],
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic
}

# Create Kafka consumer
consumer = Consumer(kafka_consumer_config)

# Subscribe to the intraday topic
consumer.subscribe(['intraday-data'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)  # Poll for new messages
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition, the consumer reached the end of the topic
                continue
            else:
                # Handle other Kafka errors
                raise KafkaException(msg.error())
        # Print the key and value of the message
        print('Received message: {0}'.format(msg.value().decode('utf-8')))
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    pass
finally:
    # Close the consumer
    consumer.close()