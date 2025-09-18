from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import time
import random
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDataProducer:
    def __init__(self, bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')):
        self.bootstrap_servers = bootstrap_servers
        self.topic = 'sensor-data'
        try:
            # Initialize Kafka admin client
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='sensor-producer'
            )

            # Initialize Kafka producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )

            # Create topic if not exists
            self.create_topic()

            logger.info(f"Producer initialized with servers: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize producer: {e}")
            raise

    def create_topic(self):
        try:
            topic_list = [NewTopic(name=self.topic, num_partitions=1, replication_factor=2)]
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
            logger.info(f"Topic '{self.topic}' created successfully.")
        except Exception as e:
            if "TopicAlreadyExistsError" in str(e):
                logger.info(f"Topic '{self.topic}' already exists.")
            else:
                logger.error(f"Failed to create topic: {e}")
                raise

    def generate_sensor_data(self):
        """Generate sample sensor data"""
        return {
            'sensor_id': f'sensor_{random.randint(1, 10)}',
            'temperature': round(random.uniform(15.0, 35.0), 2),
            'humidity': round(random.uniform(20.0, 80.0), 2),
            'pressure': round(random.uniform(980.0, 1050.0), 2),
            'location': random.choice(['warehouse_a', 'warehouse_b', 'factory_floor', 'office']),
            'timestamp': datetime.now().isoformat()
        }

    def start_producing(self, interval=5):
        """Start producing messages"""
        logger.info("Starting Kafka Producer...")
        try:
            while True:
                data = self.generate_sensor_data()

                # Send message with sensor_id as key for partitioning
                future = self.producer.send(
                    self.topic, 
                    key=data['sensor_id'],
                    value=data
                )

                # Wait for message to be sent
                record_metadata = future.get(timeout=10)
                logger.info(f"Sent to topic: {record_metadata.topic}, "
                            f"partition: {record_metadata.partition}, "
                            f"offset: {record_metadata.offset}")
                logger.info(f"Data: {data}")

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Producer stopped by user")
        except Exception as e:
            logger.error(f"Producer error: {e}")
        finally:
            self.producer.close()

if __name__ == "__main__":
    producer = SensorDataProducer()
    producer.start_producing()
