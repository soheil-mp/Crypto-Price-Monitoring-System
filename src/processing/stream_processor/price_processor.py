"""
Stream processor for real-time cryptocurrency price analytics.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from kafka import KafkaConsumer, KafkaProducer
from collections import defaultdict
import threading
import queue
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceAnalytics:
    """Price analytics calculator."""
    
    def __init__(self, window_size: int = 300):  # 5 minutes in seconds
        self.window_size = window_size
        self.price_windows = defaultdict(list)
        self.last_price = {}
        self.last_alert = {}
        
    def add_price(self, symbol: str, price: float, timestamp: datetime) -> List[Dict]:
        """
        Add a new price point and calculate analytics.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            timestamp: Price timestamp
            
        Returns:
            List of analytics results
        """
        results = []
        logger.info(f"Processing price for {symbol}: ${price:.2f} at {timestamp}")
        
        # Store price in window
        self.price_windows[symbol].append((timestamp, price))
        
        # Remove old prices from window
        cutoff_time = timestamp - timedelta(seconds=self.window_size)
        self.price_windows[symbol] = [
            (ts, p) for ts, p in self.price_windows[symbol]
            if ts > cutoff_time
        ]
        
        # Calculate analytics
        if len(self.price_windows[symbol]) > 1:
            window_prices = [p for _, p in self.price_windows[symbol]]
            analytics = {
                "symbol": symbol,
                "timestamp": timestamp.isoformat(),
                "window_start": self.price_windows[symbol][0][0].isoformat(),
                "window_end": timestamp.isoformat(),
                "average_price": statistics.mean(window_prices),
                "min_price": min(window_prices),
                "max_price": max(window_prices),
                "std_dev": statistics.stdev(window_prices) if len(window_prices) > 1 else 0,
                "num_samples": len(window_prices)
            }
            results.append(("analytics", analytics))
            logger.info(f"Analytics for {symbol}: avg=${analytics['average_price']:.2f}, "
                       f"min=${analytics['min_price']:.2f}, max=${analytics['max_price']:.2f}")
        
        # Check for significant price changes
        if symbol in self.last_price:
            price_change = (price - self.last_price[symbol]) / self.last_price[symbol]
            
            # Alert if price changed by more than 2% and no alert in last minute
            if abs(price_change) >= 0.02 and (
                symbol not in self.last_alert or
                timestamp - self.last_alert[symbol] >= timedelta(minutes=1)
            ):
                direction = "increased" if price_change > 0 else "decreased"
                alert = {
                    "symbol": symbol,
                    "timestamp": timestamp.isoformat(),
                    "price": price,
                    "previous_price": self.last_price[symbol],
                    "change_percent": price_change * 100,
                    "alert_type": f"Price {direction} by {abs(price_change)*100:.2f}%"
                }
                results.append(("alert", alert))
                self.last_alert[symbol] = timestamp
                logger.info(f"ALERT: {symbol} {alert['alert_type']} to ${price:.2f}")
        
        self.last_price[symbol] = price
        return results

class PriceProcessor:
    """Real-time price processor using Kafka streams."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        input_topic_prefix: str = "crypto_prices",
        alert_topic: str = "crypto_alerts",
        analytics_topic: str = "crypto_analytics",
        symbols: List[str] = None
    ):
        """
        Initialize the price processor.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            input_topic_prefix: Prefix for input topics
            alert_topic: Topic for price alerts
            analytics_topic: Topic for price analytics
            symbols: List of symbols to process (e.g. ["btcusdt", "ethusdt"])
        """
        self.bootstrap_servers = bootstrap_servers
        self.input_topics = [f"{input_topic_prefix}.{symbol}" for symbol in symbols] if symbols else []
        self.alert_topic = alert_topic
        self.analytics_topic = analytics_topic
        
        self.consumer = None
        self.producer = None
        self.analytics = PriceAnalytics()
        self.running = False
        self.process_thread = None
        self.message_queue = queue.Queue(maxsize=1000)
        
    def connect(self) -> bool:
        """
        Connect to Kafka brokers.
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Create consumer
            self.consumer = KafkaConsumer(
                *self.input_topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='price_processor'
            )
            
            # Create producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            logger.info(f"Connected to Kafka brokers at {self.bootstrap_servers}")
            logger.info(f"Listening to topics: {', '.join(self.input_topics)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
            
    def process_message(self, message):
        """Process a single message."""
        try:
            # Parse message
            data = message.value
            symbol = data['symbol'].lower()
            price = float(data['price'])
            timestamp = datetime.fromisoformat(data['timestamp'])
            
            # Calculate analytics
            results = self.analytics.add_price(symbol, price, timestamp)
            
            # Send results to appropriate topics
            for result_type, result in results:
                topic = self.alert_topic if result_type == "alert" else self.analytics_topic
                self.producer.send(topic, value=result)
                logger.info(f"Sent {result_type} to topic {topic}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def message_handler(self):
        """Handle messages from the queue."""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                self.process_message(message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                
    def start(self):
        """Start processing messages."""
        if not self.consumer or not self.producer:
            if not self.connect():
                return False
                
        self.running = True
        
        # Start message handler thread
        self.process_thread = threading.Thread(target=self.message_handler)
        self.process_thread.daemon = True
        self.process_thread.start()
        
        # Main loop
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                try:
                    self.message_queue.put(message, timeout=1.0)
                except queue.Full:
                    logger.warning("Message queue full, dropping message")
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.running = False
            
        return True
        
    def stop(self):
        """Stop processing messages."""
        self.running = False
        
        if self.process_thread:
            self.process_thread.join(timeout=5.0)
            
        if self.consumer:
            self.consumer.close()
            
        if self.producer:
            self.producer.close()
            
        logger.info("Processor stopped") 