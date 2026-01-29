from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime
import logging
import signal
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDataConsumer:
    def __init__(self, bootstrap_servers=None, group_id='sensor-consumer-group'):
        # Read Kafka servers from env or default
        self.bootstrap_servers = bootstrap_servers or os.environ.get(
            'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')
        self.group_id = group_id
        self.topic = 'sensor-data'
        self.running = True

        # Database configuration
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'database': os.environ.get('DB_NAME', 'sensor_db'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', 'password'),
            'port': os.environ.get('DB_PORT', '5432')
        }

        # Initialize database table
        self.init_database()

        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        logger.info(f"Consumer initialized for topic: {self.topic}")

        # Graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        logger.info("Received shutdown signal. Closing consumer...")
        self.running = False
        self.consumer.close()
        sys.exit(0)

    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def init_database(self):
        """Initialize database tables"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    sensor_id VARCHAR(50) NOT NULL,
                    temperature FLOAT,
                    humidity FLOAT,
                    pressure FLOAT,
                    location VARCHAR(100),
                    timestamp TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor_data(sensor_id);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp);
            """)
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def store_data(self, data):
        """Store consumed data to database"""
        try:
            if not isinstance(data, dict):
                logger.error(f"Invalid data format: {data}")
                return

            conn = self.get_db_connection()
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO sensor_data (sensor_id, temperature, humidity, pressure, location, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            # Parse timestamp safely
            ts = data.get('timestamp')
            timestamp = datetime.fromisoformat(ts.replace('Z', '+00:00')) if ts else datetime.now()

            cursor.execute(insert_query, (
                data.get('sensor_id'),
                data.get('temperature'),
                data.get('humidity'),
                data.get('pressure'),
                data.get('location'),
                timestamp
            ))

            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Stored data for sensor: {data.get('sensor_id')}")

        except Exception as e:
            logger.error(f"Database storage error: {e}")

    def start_consuming(self):
        """Start consuming messages"""
        logger.info("Starting Kafka consumer...")
        try:
            for message in self.consumer:
                if not self.running:
                    break

                try:
                    data = message.value  # Already deserialized by value_deserializer
                    logger.info(f"Consumed message - Key: {message.key}, Partition: {message.partition}, Offset: {message.offset}")
                    logger.info(f"Data: {data}")
                    self.store_data(data)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    consumer = SensorDataConsumer()
    consumer.start_consuming()
