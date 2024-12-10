"""
Alert processor for monitoring cryptocurrency prices and generating alerts.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertProcessor:
    def __init__(self, 
                 bootstrap_servers: str = 'localhost:9092',
                 price_topics: List[str] = None,
                 alert_topic: str = 'crypto_alerts',
                 consumer_group: str = 'alert_processor'):
        """
        Initialize the alert processor.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            price_topics: List of price topics to monitor
            alert_topic: Topic to publish alerts to
            consumer_group: Consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers
        self.price_topics = price_topics or []
        self.alert_topic = alert_topic
        self.consumer_group = consumer_group
        
        # Alert thresholds
        self.price_thresholds: Dict[str, Dict[str, float]] = {
            'btcusdt': {'high': 100000.0, 'low': 95000.0},
            'ethusdt': {'high': 4000.0, 'low': 3800.0},
            'solusdt': {'high': 240.0, 'low': 230.0},
            'adausdt': {'high': 1.25, 'low': 1.15}
        }
        
        # Volatility thresholds (percentage change)
        self.volatility_threshold = 0.02  # 2% change
        
        # Price history for volatility calculation
        self.price_history: Dict[str, List[float]] = {}
        self.history_size = 10  # Number of prices to keep for each symbol
        
        # Initialize Kafka consumer and producer
        self.consumer = None
        self.producer = None
        
    def connect(self) -> bool:
        """
        Connect to Kafka broker.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Initialize consumer
            self.consumer = KafkaConsumer(
                *self.price_topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest'
            )
            
            # Initialize producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            logger.info(f"Monitoring topics: {', '.join(self.price_topics)}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
            
    def check_price_threshold(self, symbol: str, price: float) -> Optional[Dict]:
        """
        Check if price crosses any thresholds.
        
        Args:
            symbol: Cryptocurrency symbol
            price: Current price
            
        Returns:
            Optional[Dict]: Alert message if threshold crossed, None otherwise
        """
        if symbol not in self.price_thresholds:
            return None
            
        thresholds = self.price_thresholds[symbol]
        
        if price >= thresholds['high']:
            return {
                'type': 'threshold',
                'symbol': symbol,
                'price': price,
                'threshold': thresholds['high'],
                'direction': 'above',
                'timestamp': datetime.now().isoformat()
            }
        elif price <= thresholds['low']:
            return {
                'type': 'threshold',
                'symbol': symbol,
                'price': price,
                'threshold': thresholds['low'],
                'direction': 'below',
                'timestamp': datetime.now().isoformat()
            }
            
        return None
        
    def check_volatility(self, symbol: str, price: float) -> Optional[Dict]:
        """
        Check for significant price volatility.
        
        Args:
            symbol: Cryptocurrency symbol
            price: Current price
            
        Returns:
            Optional[Dict]: Alert message if volatility detected, None otherwise
        """
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            
        history = self.price_history[symbol]
        history.append(price)
        
        # Keep only recent prices
        if len(history) > self.history_size:
            history.pop(0)
            
        # Need at least 2 prices to calculate volatility
        if len(history) < 2:
            return None
            
        # Calculate percentage change
        prev_price = history[-2]
        pct_change = abs(price - prev_price) / prev_price
        
        if pct_change >= self.volatility_threshold:
            return {
                'type': 'volatility',
                'symbol': symbol,
                'price': price,
                'previous_price': prev_price,
                'change_percent': round(pct_change * 100, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        return None
        
    def send_alert(self, alert: Dict) -> bool:
        """
        Send alert to Kafka topic.
        
        Args:
            alert: Alert message
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            future = self.producer.send(self.alert_topic, value=alert)
            future.get(timeout=10)
            logger.info(f"Alert sent: {alert}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send alert: {e}")
            return False
            
    def process_message(self, message) -> None:
        """
        Process a single price message.
        
        Args:
            message: Kafka message containing price data
        """
        try:
            data = message.value
            symbol = data['symbol'].lower()
            price = float(data['price'])
            
            # Check price thresholds
            threshold_alert = self.check_price_threshold(symbol, price)
            if threshold_alert:
                self.send_alert(threshold_alert)
                
            # Check volatility
            volatility_alert = self.check_volatility(symbol, price)
            if volatility_alert:
                self.send_alert(volatility_alert)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def run(self) -> None:
        """Run the alert processor."""
        if not self.consumer:
            logger.error("Not connected to Kafka")
            return
            
        try:
            logger.info("Starting alert processor...")
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            logger.info("Shutting down alert processor...")
        except Exception as e:
            logger.error(f"Error in alert processor: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
            if self.producer:
                self.producer.close() 