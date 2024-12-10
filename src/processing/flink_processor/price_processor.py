"""
Apache Flink processor for real-time cryptocurrency price analytics.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.window import TumblingEventTimeWindows, Time
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction, WindowFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.time import Duration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimestampAssigner(MapFunction):
    """Assigns timestamps and watermarks to incoming records."""
    
    def map(self, value: str) -> Tuple[str, float, int]:
        """
        Extract timestamp from record for event time processing.
        
        Args:
            value: JSON string containing crypto price data
            
        Returns:
            Tuple of (symbol, price, timestamp)
        """
        try:
            data = json.loads(value)
            symbol = data['symbol']
            price = float(data['price'])
            timestamp = int(datetime.fromisoformat(data['timestamp']).timestamp() * 1000)
            return symbol, price, timestamp
        except Exception as e:
            logger.error(f"Error parsing record: {e}")
            return None

class PriceAnalyzer(KeyedProcessFunction):
    """Analyzes price movements and detects significant changes."""
    
    def __init__(self, threshold: float = 0.02):  # 2% threshold
        self.threshold = threshold
        self.last_price = {}
        self.last_alert = {}
        
    def process_element(self, value: Tuple[str, float, int], ctx: KeyedProcessFunction.Context):
        """
        Process each price record and detect significant changes.
        
        Args:
            value: Tuple of (symbol, price, timestamp)
            ctx: Processing context
        """
        symbol, price, timestamp = value
        
        if symbol not in self.last_price:
            self.last_price[symbol] = price
            self.last_alert[symbol] = timestamp
            return
            
        price_change = (price - self.last_price[symbol]) / self.last_price[symbol]
        
        # Check if change exceeds threshold and we haven't alerted recently
        if abs(price_change) >= self.threshold and \
           timestamp - self.last_alert[symbol] >= 60000:  # 1 minute minimum between alerts
            
            direction = "increased" if price_change > 0 else "decreased"
            alert = {
                "symbol": symbol,
                "timestamp": datetime.fromtimestamp(timestamp / 1000).isoformat(),
                "price": price,
                "previous_price": self.last_price[symbol],
                "change_percent": price_change * 100,
                "alert_type": f"Price {direction} by {abs(price_change)*100:.2f}%"
            }
            
            # Emit alert
            yield json.dumps(alert)
            
            # Update last alert time
            self.last_alert[symbol] = timestamp
            
        # Always update last price
        self.last_price[symbol] = price

class MovingAverageWindow(WindowFunction):
    """Calculates moving averages over price windows."""
    
    def apply(self, key: str, window: TumblingEventTimeWindows, inputs: List[Tuple[str, float, int]], out):
        """
        Calculate moving average for the window.
        
        Args:
            key: Symbol
            window: Time window
            inputs: List of price records
            out: Output collector
        """
        if not inputs:
            return
            
        prices = [x[1] for x in inputs]
        avg_price = sum(prices) / len(prices)
        timestamp = inputs[-1][2]  # Use latest timestamp
        
        result = {
            "symbol": key,
            "timestamp": datetime.fromtimestamp(timestamp / 1000).isoformat(),
            "window_start": datetime.fromtimestamp(window.start / 1000).isoformat(),
            "window_end": datetime.fromtimestamp(window.end / 1000).isoformat(),
            "average_price": avg_price,
            "num_samples": len(prices)
        }
        
        out.collect(json.dumps(result))

def create_flink_job(
    kafka_bootstrap_servers: str,
    input_topics: List[str],
    alert_topic: str,
    analytics_topic: str
) -> None:
    """
    Create and execute the Flink streaming job.
    
    Args:
        kafka_bootstrap_servers: Kafka bootstrap servers
        input_topics: List of input topics to consume from
        alert_topic: Topic to publish price alerts to
        analytics_topic: Topic to publish analytics results to
    """
    # Create execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    env.enable_checkpointing(60000)  # Checkpoint every minute
    
    # Properties for Kafka consumer
    props = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': 'flink_price_processor'
    }
    
    # Create Kafka consumer
    kafka_consumer = FlinkKafkaConsumer(
        topics=input_topics,
        deserialization_schema=SimpleStringSchema(),
        properties=props
    )
    
    # Create Kafka producers
    alert_producer = FlinkKafkaProducer(
        topic=alert_topic,
        serialization_schema=SimpleStringSchema(),
        producer_config=props
    )
    
    analytics_producer = FlinkKafkaProducer(
        topic=analytics_topic,
        serialization_schema=SimpleStringSchema(),
        producer_config=props
    )
    
    # Create the processing pipeline
    stream = env.add_source(kafka_consumer)
    
    # Parse and assign timestamps
    parsed_stream = stream \
        .map(TimestampAssigner()) \
        .filter(lambda x: x is not None) \
        .assign_timestamps_and_watermarks(
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
            .with_timestamp_assigner(lambda event, timestamp: event[2])
        )
    
    # Price change detection
    parsed_stream \
        .key_by(lambda x: x[0]) \
        .process(PriceAnalyzer()) \
        .add_sink(alert_producer)
    
    # Moving average calculation
    parsed_stream \
        .key_by(lambda x: x[0]) \
        .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
        .apply(MovingAverageWindow()) \
        .add_sink(analytics_producer)
    
    # Execute the job
    env.execute("Crypto Price Analytics")

if __name__ == "__main__":
    # Example usage
    create_flink_job(
        kafka_bootstrap_servers="localhost:9092",
        input_topics=["crypto_prices.btcusdt", "crypto_prices.ethusdt", "crypto_prices.solusdt", "crypto_prices.adausdt"],
        alert_topic="crypto_alerts",
        analytics_topic="crypto_analytics"
    ) 