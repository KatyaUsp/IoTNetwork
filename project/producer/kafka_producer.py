# producer/kafka_producer.py

from kafka import KafkaProducer
import pandas as pd
import json
import time
import sys
from kafka.errors import NoBrokersAvailable

def main():
    # Initialize Kafka Producer with retry logic
    max_retries = 10
    retry_delay = 5  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Connected to Kafka broker.")
            break
        except NoBrokersAvailable:
            print(f"Attempt {attempt} of {max_retries}: Kafka broker not available. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    else:
        print("Failed to connect to Kafka broker after multiple attempts. Exiting.")
        sys.exit(1)

    # Read the dataset
    df = pd.read_csv('/data/iot_network_intrusion_dataset.csv')

    # Stream data to Kafka topic
    for index, row in df.iterrows():
        data = row.to_dict()
        producer.send('iot_topic', value=data)
        time.sleep(0.1)  # Adjust the sleep time as needed

    producer.flush()
    producer.close()

if __name__ == "__main__":
    main()
