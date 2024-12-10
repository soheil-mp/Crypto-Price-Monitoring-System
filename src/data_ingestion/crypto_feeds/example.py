"""
Example usage of the CryptoFeedClient with Kafka integration.
"""
import asyncio
import logging
import signal
from .feed_client import CryptoFeedClient
from ..kafka_producer.crypto_producer import CryptoKafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for cleanup
client = None
kafka_producer = None
shutdown_event = asyncio.Event()

async def handle_crypto_data(data):
    """
    Example callback function to handle received crypto data.
    
    Args:
        data: Cleaned cryptocurrency data dictionary
    """
    global kafka_producer
    
    # Log the received data
    logger.info(f"Received {data['symbol']} price: ${data['price']:.2f} at {data['timestamp']}")
    
    # Send data to Kafka if producer is available
    if kafka_producer:
        success = kafka_producer.send(data)
        if not success:
            logger.error(f"Failed to send data to Kafka for {data['symbol']}")

async def shutdown(sig, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {sig.name}...")
    shutdown_event.set()
    
    # Close WebSocket client
    if client:
        logger.info("Closing WebSocket connection...")
        await client.close()
    
    # Close Kafka producer
    if kafka_producer:
        logger.info("Closing Kafka producer...")
        kafka_producer.close()
        
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if tasks:
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

def handle_exception(loop, context):
    """Handle exceptions that escape the async tasks."""
    # Don't log cancelled errors during shutdown
    if "exception" in context and isinstance(context["exception"], asyncio.CancelledError):
        if not shutdown_event.is_set():
            logger.error("Task cancelled unexpectedly")
        return
        
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception: {msg}")

async def run_client():
    """Run the crypto feed client."""
    global client, kafka_producer
    
    try:
        # Initialize Kafka producer
        kafka_producer = CryptoKafkaProducer()
        if not kafka_producer.connect():
            logger.error("Failed to connect to Kafka. Continuing without Kafka integration.")
            kafka_producer = None
        
        # Initialize the client with some popular cryptocurrency pairs
        symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD"]
        client = CryptoFeedClient(symbols=symbols, on_message_callback=handle_crypto_data)
        
        # Connect to the WebSocket feed
        await client.connect()
    except asyncio.CancelledError:
        logger.info("Client task cancelled")
    except Exception as e:
        logger.error(f"Error in client: {e}")
    finally:
        if client:
            await client.close()
        if kafka_producer:
            kafka_producer.close()
    return True

async def main_async():
    """Async main function."""
    # Create and run the client task
    client_task = asyncio.create_task(run_client())
    
    try:
        # Wait for the client task to complete or be cancelled
        await client_task
    except asyncio.CancelledError:
        # Handle graceful shutdown
        if not client_task.done():
            client_task.cancel()
            await asyncio.wait([client_task])

def main():
    """Main entry point."""
    # Create and configure event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Handle exceptions
    loop.set_exception_handler(handle_exception)
    
    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )
    
    try:
        loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Clean up
        try:
            pending = asyncio.all_tasks(loop)
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            logger.info("Successfully shutdown the crypto feed service.")

if __name__ == "__main__":
    main() 