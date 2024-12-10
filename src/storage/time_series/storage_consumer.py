"""
Kafka consumer for storing cryptocurrency data.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from kafka import KafkaConsumer
from .price_store import PriceStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageConsumer:
    """Consumer for storing cryptocurrency data from Kafka."""
    
    def __init__(
        self,
        price_store: PriceStore,
        bootstrap_servers: str = "localhost:9092",
        price_topics: Optional[List[str]] = None,
        analytics_topic: str = "crypto_analytics",
        alerts_topic: str = "crypto_alerts"
    ):
        """
        Initialize the storage consumer.
        
        Args:
            price_store: PriceStore instance for data storage
            bootstrap_servers: Kafka bootstrap servers
            price_topics: List of price topics to consume
            analytics_topic: Topic for analytics data
            alerts_topic: Topic for alert data
        """
        self.price_store = price_store
        self.bootstrap_servers = bootstrap_servers
        self.price_topics = price_topics or []
        self.analytics_topic = analytics_topic
        self.alerts_topic = alerts_topic
        
        self.consumer = None
        self.running = False
        
    def connect(self) -> bool:
        """
        Connect to Kafka broker.
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Create topics list
            topics = self.price_topics + [self.analytics_topic, self.alerts_topic]
            
            # Create consumer
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='storage_consumer'
            )
            
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            logger.info(f"Listening to topics: {', '.join(topics)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
            
    def process_message(self, topic: str, message: Dict) -> bool:
        """
        Process and store a message based on its topic.
        
        Args:
            topic: Kafka topic
            message: Message data
            
        Returns:
            bool: True if processing successful
        """
        try:
            # Extract symbol from topic for price data
            if topic in self.price_topics:
                symbol = topic.split('.')[-1]  # e.g., "crypto_prices.btcusdt" -> "btcusdt"
                return self.price_store.store_raw_price(symbol, message)
                
            # For analytics and alerts, symbol is in the message
            symbol = message.get('symbol', '').lower()
            if not symbol:
                logger.error(f"No symbol in message for topic {topic}")
                return False
                
            if topic == self.analytics_topic:
                return self.price_store.store_analytics(symbol, message)
                
            if topic == self.alerts_topic:
                return self.price_store.store_alert(symbol, message)
                
            logger.warning(f"Unknown topic: {topic}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
            
    def start(self):
        """Start consuming and storing messages."""
        if not self.consumer:
            if not self.connect():
                return
                
        self.running = True
        logger.info("Starting storage consumer...")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                topic = message.topic
                data = message.value
                
                if self.process_message(topic, data):
                    logger.debug(f"Successfully processed message from topic {topic}")
                else:
                    logger.warning(f"Failed to process message from topic {topic}")
                    
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            self.running = False
            
        finally:
            self.stop()
            
    def stop(self):
        """Stop the consumer."""
        self.running = False
        
        if self.consumer:
            self.consumer.close()
            logger.info("Storage consumer stopped") 