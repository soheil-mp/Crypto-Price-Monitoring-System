"""
Kafka producer for streaming cryptocurrency data.
"""
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class CryptoKafkaProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092', topic_prefix: str = 'crypto_prices'):
        """
        Initialize the Kafka producer for cryptocurrency data.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic_prefix: Prefix for Kafka topics (final topic will be {prefix}.{symbol})
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self.producer: Optional[KafkaProducer] = None
        
    def connect(self) -> bool:
        """
        Connect to Kafka broker.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, cls=DateTimeEncoder).encode('utf-8'),
                key_serializer=lambda v: v.encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3,   # Retry on failure
                max_in_flight_requests_per_connection=1  # Preserve order
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka broker: {e}")
            return False
            
    def send(self, data: Dict) -> bool:
        """
        Send cryptocurrency data to Kafka.
        
        Args:
            data: Dictionary containing cryptocurrency data
            
        Returns:
            bool: True if send successful, False otherwise
        """
        if not self.producer:
            logger.error("Producer not connected")
            return False
            
        try:
            # Extract symbol and create topic name
            symbol = data.get('symbol', '').lower()
            if not symbol:
                logger.error("No symbol in data")
                return False
                
            topic = f"{self.topic_prefix}.{symbol}"
            
            # Send data to Kafka
            future = self.producer.send(
                topic=topic,
                key=symbol,
                value=data
            )
            
            # Wait for the send to complete
            future.get(timeout=10)
            logger.debug(f"Sent data to topic {topic}: {data}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send data to Kafka: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending data to Kafka: {e}")
            return False
            
    def close(self):
        """Close the Kafka producer."""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
            self.producer = None 