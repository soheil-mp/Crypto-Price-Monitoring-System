#!/bin/bash

echo "Setting up Crypto Price Monitoring System..."

# Clean up existing environment
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cat > .env << EOL
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=crypto_prices
KAFKA_ANOMALY_TOPIC=price_anomalies

# Crypto Configuration
CRYPTO_SYMBOLS=BTC-USD,ETH-USD,XRP-USD
UPDATE_INTERVAL=60
EOL
fi

# Start Kafka and Zookeeper
echo "Starting Kafka and Zookeeper..."
docker-compose down
docker-compose up -d

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 10

# Create Kafka topics
echo "Creating Kafka topics..."
docker-compose exec -T kafka kafka-topics.sh \
    --create --if-not-exists \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic crypto_prices

docker-compose exec -T kafka kafka-topics.sh \
    --create --if-not-exists \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic price_anomalies

echo "Setup completed successfully!"
echo "Next steps:"
echo "1. Update the .env file with your Discord bot token and channel ID"
echo "2. Start the components in the following order:"
echo "   - Crypto price producer"
echo "   - Stream processor"
echo "   - Anomaly detector"
echo "   - Discord bot" 