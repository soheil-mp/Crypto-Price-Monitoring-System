import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import json
from typing import List, Dict, Optional
import logging
from datetime import datetime
import pandas as pd
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceAnomalyDetector:
    def __init__(
        self,
        bootstrap_servers: List[str],
        input_topic: str,
        output_topic: str,
        window_size: int = 60,
        z_score_threshold: float = 3.0
    ):
        """
        Initialize the Price Anomaly Detector.
        
        Args:
            bootstrap_servers: List of Kafka broker addresses
            input_topic: Topic to consume processed price data from
            output_topic: Topic to publish anomaly alerts to
            window_size: Size of the rolling window for calculations (in minutes)
            z_score_threshold: Z-score threshold for anomaly detection
        """
        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='price_anomaly_detector'
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        self.output_topic = output_topic
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.price_history: Dict[str, List[float]] = {}
        self.moving_avg_history: Dict[str, List[float]] = {}

    def calculate_z_score(self, values: List[float]) -> Optional[float]:
        """Calculate z-score for the latest value."""
        if len(values) < 2:
            return None
        
        recent_values = values[-self.window_size:]
        if len(recent_values) < 2:
            return None
            
        mean = np.mean(recent_values[:-1])
        std = np.std(recent_values[:-1])
        
        if std == 0:
            return 0.0
            
        return (recent_values[-1] - mean) / std

    def detect_anomalies(self, data: Dict) -> Optional[Dict]:
        """
        Detect price anomalies using statistical methods.
        
        Uses both Z-score and price change percentage to detect anomalies.
        """
        symbol = data['symbol']
        current_price = data['price']
        moving_avg = data['moving_avg']
        price_change_pct = data['price_change_pct']
        
        # Initialize history for new symbols
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.moving_avg_history[symbol] = []
        
        # Update history
        self.price_history[symbol].append(current_price)
        self.moving_avg_history[symbol].append(moving_avg)
        
        # Keep only window_size latest values
        self.price_history[symbol] = self.price_history[symbol][-self.window_size:]
        self.moving_avg_history[symbol] = self.moving_avg_history[symbol][-self.window_size:]
        
        # Calculate z-scores
        price_z_score = self.calculate_z_score(self.price_history[symbol])
        
        if price_z_score is None:
            return None
            
        # Check for anomalies
        is_anomaly = (
            abs(price_z_score) > self.z_score_threshold or
            abs(price_change_pct) > 5.0  # Alert if price changes more than 5% in a minute
        )
        
        if is_anomaly:
            return {
                'symbol': symbol,
                'timestamp': data['timestamp'],
                'current_price': current_price,
                'moving_average': moving_avg,
                'price_change_pct': price_change_pct,
                'z_score': price_z_score,
                'anomaly_type': 'price_movement',
                'severity': 'high' if abs(price_z_score) > 2 * self.z_score_threshold else 'medium'
            }
        
        return None

    def run(self):
        """Run the anomaly detection process."""
        logger.info("Starting anomaly detection process...")
        
        try:
            for message in self.consumer:
                data = message.value
                
                anomaly = self.detect_anomalies(data)
                if anomaly:
                    logger.info(f"Anomaly detected for {anomaly['symbol']}: {anomaly}")
                    self.producer.send(self.output_topic, value=anomaly)
                    self.producer.flush()
                    
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    detector = PriceAnomalyDetector(
        bootstrap_servers=['localhost:9092'],
        input_topic='processed_crypto_prices',
        output_topic='crypto_price_anomalies',
        window_size=60,  # 1 hour window
        z_score_threshold=3.0
    )
    detector.run() 