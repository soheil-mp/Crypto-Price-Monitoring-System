import discord
from discord.ext import commands, tasks
from kafka import KafkaConsumer
import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAlertBot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        alert_channel_id: int,
        bootstrap_servers: list,
        topic: str
    ):
        """
        Initialize the Crypto Alert Bot.
        
        Args:
            command_prefix: Command prefix for bot commands
            alert_channel_id: Discord channel ID for sending alerts
            bootstrap_servers: List of Kafka broker addresses
            topic: Kafka topic to consume anomaly alerts from
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.alert_channel_id = alert_channel_id
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='discord_alert_bot'
        )
        
        # Start the alert checking loop
        self.check_alerts.start()

    async def setup_hook(self):
        """Set up the bot with initial commands."""
        @self.command(name='status')
        async def status(ctx):
            """Check if the bot is running and monitoring alerts."""
            await ctx.send("🟢 Bot is running and monitoring crypto price anomalies!")

        @self.command(name='help')
        async def help_command(ctx):
            """Display help information."""
            help_text = """
            **Crypto Alert Bot Commands**
            `!status` - Check if the bot is running
            `!help` - Display this help message
            
            The bot automatically sends alerts when crypto price anomalies are detected.
            """
            await ctx.send(help_text)

    def format_alert_message(self, alert_data: Dict) -> str:
        """Format the alert data into a Discord message."""
        severity_emoji = "🔴" if alert_data['severity'] == 'high' else "🟡"
        
        return f"""
{severity_emoji} **Crypto Price Anomaly Detected!**

**Symbol:** {alert_data['symbol']}
**Current Price:** ${alert_data['current_price']:.2f}
**Price Change:** {alert_data['price_change_pct']:.2f}%
**Z-Score:** {alert_data['z_score']:.2f}
**Severity:** {alert_data['severity'].upper()}
**Time:** {datetime.fromisoformat(alert_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC')}

{'⚠️ **URGENT:** Extreme price movement detected!' if alert_data['severity'] == 'high' else ''}
"""

    @tasks.loop(seconds=1)
    async def check_alerts(self):
        """Check for new alerts from Kafka and send them to Discord."""
        try:
            # Wait until the bot is ready
            await self.wait_until_ready()
            
            # Get the alert channel
            channel = self.get_channel(self.alert_channel_id)
            if not channel:
                logger.error(f"Could not find channel with ID {self.alert_channel_id}")
                return
            
            # Check for new messages
            for message in self.consumer:
                alert_data = message.value
                alert_message = self.format_alert_message(alert_data)
                
                try:
                    await channel.send(alert_message)
                    logger.info(f"Sent alert for {alert_data['symbol']}")
                except Exception as e:
                    logger.error(f"Error sending Discord message: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in check_alerts: {str(e)}")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user.name}")
        logger.info("Bot is ready to send alerts!")

def run_bot():
    """Run the Discord bot."""
    # Get configuration from environment variables
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
    KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')
    
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN environment variable is not set")
    
    if not CHANNEL_ID:
        raise ValueError("DISCORD_CHANNEL_ID environment variable is not set")
    
    # Create and run the bot
    bot = CryptoAlertBot(
        command_prefix="!",
        alert_channel_id=CHANNEL_ID,
        bootstrap_servers=KAFKA_SERVERS,
        topic='crypto_price_anomalies'
    )
    
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot() 