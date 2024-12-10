"""
Real-time data streaming module for Tableau.
"""
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from kafka import KafkaConsumer
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableauStreamer:
    """Stream real-time data to Tableau."""
    
    def __init__(
        self,
        export_dir: Path,
        bootstrap_servers: str = 'localhost:9092',
        price_topics: Optional[List[str]] = None,
        analytics_topic: str = 'crypto_analytics',
        alerts_topic: str = 'crypto_alerts',
        max_buffer_size: int = 1000,
        export_interval: int = 15  # seconds
    ):
        """
        Initialize the Tableau streamer.
        
        Args:
            export_dir: Directory for exported files
            bootstrap_servers: Kafka bootstrap servers
            price_topics: List of price topics to monitor
            analytics_topic: Topic for analytics data
            alerts_topic: Topic for alerts
            max_buffer_size: Maximum number of records to buffer
            export_interval: How often to export data (seconds)
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        self.bootstrap_servers = bootstrap_servers
        self.price_topics = price_topics or []
        self.analytics_topic = analytics_topic
        self.alerts_topic = alerts_topic
        
        self.max_buffer_size = max_buffer_size
        self.export_interval = export_interval
        
        # Data buffers
        self.price_buffer = []
        self.analytics_buffer = []
        self.alerts_buffer = []
        
        # Threading controls
        self.running = False
        self.export_thread = None
        self.consumer_threads = []
        
        # Locks for thread safety
        self.price_lock = threading.Lock()
        self.analytics_lock = threading.Lock()
        self.alerts_lock = threading.Lock()
        
    def _consume_prices(self):
        """Consume price data from Kafka."""
        try:
            consumer = KafkaConsumer(
                *self.price_topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='tableau_price_streamer'
            )
            
            for message in consumer:
                if not self.running:
                    break
                    
                with self.price_lock:
                    self.price_buffer.append(message.value)
                    if len(self.price_buffer) > self.max_buffer_size:
                        self.price_buffer.pop(0)
                        
        except Exception as e:
            logger.error(f"Error consuming price data: {e}")
        finally:
            consumer.close()
            
    def _consume_analytics(self):
        """Consume analytics data from Kafka."""
        try:
            consumer = KafkaConsumer(
                self.analytics_topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='tableau_analytics_streamer'
            )
            
            for message in consumer:
                if not self.running:
                    break
                    
                with self.analytics_lock:
                    self.analytics_buffer.append(message.value)
                    if len(self.analytics_buffer) > self.max_buffer_size:
                        self.analytics_buffer.pop(0)
                        
        except Exception as e:
            logger.error(f"Error consuming analytics data: {e}")
        finally:
            consumer.close()
            
    def _consume_alerts(self):
        """Consume alert data from Kafka."""
        try:
            consumer = KafkaConsumer(
                self.alerts_topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='tableau_alerts_streamer'
            )
            
            for message in consumer:
                if not self.running:
                    break
                    
                with self.alerts_lock:
                    self.alerts_buffer.append(message.value)
                    if len(self.alerts_buffer) > self.max_buffer_size:
                        self.alerts_buffer.pop(0)
                        
        except Exception as e:
            logger.error(f"Error consuming alert data: {e}")
        finally:
            consumer.close()
            
    def _export_data(self):
        """Export buffered data to files."""
        while self.running:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Export price data
                with self.price_lock:
                    if self.price_buffer:
                        df = pd.DataFrame(self.price_buffer)
                        path = self.export_dir / f"realtime_prices_{timestamp}.csv"
                        df.to_csv(path, index=False)
                        logger.debug(f"Exported {len(df)} price records to {path}")
                        
                # Export analytics data
                with self.analytics_lock:
                    if self.analytics_buffer:
                        df = pd.DataFrame(self.analytics_buffer)
                        path = self.export_dir / f"realtime_analytics_{timestamp}.csv"
                        df.to_csv(path, index=False)
                        logger.debug(f"Exported {len(df)} analytics records to {path}")
                        
                # Export alerts data
                with self.alerts_lock:
                    if self.alerts_buffer:
                        df = pd.DataFrame(self.alerts_buffer)
                        path = self.export_dir / f"realtime_alerts_{timestamp}.csv"
                        df.to_csv(path, index=False)
                        logger.debug(f"Exported {len(df)} alert records to {path}")
                        
                # Clean up old files (keep last 5 minutes)
                self._cleanup_old_files()
                
            except Exception as e:
                logger.error(f"Error exporting data: {e}")
                
            time.sleep(self.export_interval)
            
    def _cleanup_old_files(self):
        """Clean up old export files."""
        try:
            current_time = time.time()
            for pattern in ["realtime_*.csv"]:
                for file_path in self.export_dir.glob(pattern):
                    if current_time - file_path.stat().st_mtime > 300:  # 5 minutes
                        file_path.unlink()
                        logger.debug(f"Cleaned up old file: {file_path}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            
    def start(self):
        """Start the streaming service."""
        if self.running:
            logger.warning("Streamer is already running")
            return
            
        self.running = True
        logger.info("Starting Tableau streamer...")
        
        # Start consumer threads
        if self.price_topics:
            thread = threading.Thread(target=self._consume_prices)
            thread.daemon = True
            thread.start()
            self.consumer_threads.append(thread)
            
        thread = threading.Thread(target=self._consume_analytics)
        thread.daemon = True
        thread.start()
        self.consumer_threads.append(thread)
        
        thread = threading.Thread(target=self._consume_alerts)
        thread.daemon = True
        thread.start()
        self.consumer_threads.append(thread)
        
        # Start export thread
        self.export_thread = threading.Thread(target=self._export_data)
        self.export_thread.daemon = True
        self.export_thread.start()
        
        logger.info("Tableau streamer started")
        
    def stop(self):
        """Stop the streaming service."""
        if not self.running:
            return
            
        self.running = False
        logger.info("Stopping Tableau streamer...")
        
        # Wait for threads to finish
        for thread in self.consumer_threads:
            thread.join(timeout=5.0)
            
        if self.export_thread:
            self.export_thread.join(timeout=5.0)
            
        logger.info("Tableau streamer stopped") 