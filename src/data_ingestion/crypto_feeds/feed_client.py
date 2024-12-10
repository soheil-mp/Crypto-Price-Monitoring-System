"""
WebSocket client for real-time cryptocurrency data feeds.
"""
import asyncio
import json
import logging
import websockets
from typing import Dict, List, Optional, Callable
from datetime import datetime
from websockets.exceptions import ConnectionClosed, WebSocketException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoFeedClient:
    def __init__(self, symbols: List[str], on_message_callback: Optional[Callable] = None):
        """
        Initialize the crypto feed client.
        
        Args:
            symbols: List of cryptocurrency symbols to monitor (e.g., ["BTCUSDT", "ETHUSDT"])
            on_message_callback: Optional callback function to handle received messages
        """
        # Convert symbols to Binance format (e.g., BTC-USD -> BTCUSDT)
        self.symbols = [s.replace("-", "").replace("USD", "USDT").lower() for s in symbols]
        self.on_message_callback = on_message_callback
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.reconnect_delay = 1  # Initial reconnect delay in seconds
        self.max_reconnect_delay = 60  # Maximum reconnect delay in seconds
        self._stop = False
        self._connection_task = None

    async def connect(self, uri: str = "wss://stream.binance.com:9443/ws"):
        """
        Establish WebSocket connection with retry mechanism.
        
        Args:
            uri: WebSocket endpoint URI
        """
        self._stop = False
        self._connection_task = asyncio.create_task(self._connection_loop(uri))
        await self._connection_task

    async def _connection_loop(self, uri: str):
        """Internal connection loop with retry mechanism."""
        while not self._stop:
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    self.is_connected = True
                    logger.info("Connected to WebSocket feed")
                    
                    # Subscribe to specified symbols
                    await self._subscribe()
                    
                    # Reset reconnect delay on successful connection
                    self.reconnect_delay = 1
                    
                    # Start message handling
                    await self._handle_messages()
                    
            except (ConnectionClosed, WebSocketException) as e:
                if self._stop:
                    break
                logger.error(f"WebSocket connection error: {e}")
                await self._handle_reconnection()
                
            except Exception as e:
                if self._stop:
                    break
                logger.error(f"Unexpected error: {e}")
                await self._handle_reconnection()
            
            finally:
                self.is_connected = False
                self.websocket = None

    async def _subscribe(self):
        """Send subscription message for specified symbols."""
        if not self.websocket or not self.is_connected:
            return
            
        # Create subscription message for each symbol
        streams = [f"{symbol}@ticker" for symbol in self.symbols]
        subscription_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        
        await self.websocket.send(json.dumps(subscription_message))
        logger.info(f"Subscribed to symbols: {self.symbols}")

    async def _handle_messages(self):
        """Handle incoming WebSocket messages."""
        if not self.websocket or not self.is_connected:
            return
            
        try:
            async for message in self.websocket:
                if self._stop:
                    break
                    
                try:
                    data = json.loads(message)
                    
                    # Skip subscription responses
                    if "result" in data:
                        continue
                    
                    # Validate and clean the data
                    cleaned_data = self._validate_and_clean_data(data)
                    
                    if cleaned_data and self.on_message_callback:
                        await self.on_message_callback(cleaned_data)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                
        except Exception as e:
            if not self._stop:
                logger.error(f"Error in message handling loop: {e}")
                raise

    def _validate_and_clean_data(self, data: Dict) -> Optional[Dict]:
        """
        Validate and clean received data.
        
        Args:
            data: Raw data received from WebSocket
            
        Returns:
            Cleaned data dictionary or None if validation fails
        """
        try:
            # Extract and validate required fields
            required_fields = ["s", "c", "E"]  # symbol, current price, event time
            if not all(field in data for field in required_fields):
                return None

            # Clean and format the data
            cleaned_data = {
                "symbol": data["s"],
                "price": float(data["c"]),  # Using 'c' (current price) instead of 'p' (price change)
                "timestamp": datetime.fromtimestamp(data["E"] / 1000),  # Convert from milliseconds
                "volume_24h": float(data.get("v", 0)),
                "sequence": int(data.get("E", 0))
            }

            return cleaned_data

        except (ValueError, KeyError) as e:
            logger.error(f"Error validating data: {e}")
            return None

    async def _handle_reconnection(self):
        """Handle reconnection with exponential backoff."""
        if self._stop:
            return
            
        self.is_connected = False
        logger.info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        
        # Implement exponential backoff
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    async def close(self):
        """Close the WebSocket connection."""
        self._stop = True
        
        if self.websocket and self.is_connected:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
            
        if self._connection_task:
            try:
                self._connection_task.cancel()
                await asyncio.gather(self._connection_task, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error cancelling connection task: {e}")
            
        self.websocket = None
        self.is_connected = False
        logger.info("WebSocket connection closed") 