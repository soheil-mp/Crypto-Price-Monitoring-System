"""
FastAPI application for serving cryptocurrency data.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kafka import KafkaConsumer
import pandas as pd

app = FastAPI(
    title="Crypto Price API",
    description="API for accessing cryptocurrency price data and analytics",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PriceData(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    
class AnalyticsData(BaseModel):
    symbol: str
    avg_price: float
    min_price: float
    max_price: float
    timestamp: datetime
    
class AlertData(BaseModel):
    type: str
    symbol: str
    price: float
    timestamp: datetime
    threshold: Optional[float] = None
    direction: Optional[str] = None
    previous_price: Optional[float] = None
    change_percent: Optional[float] = None

# Data access functions
def get_price_data(symbol: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    """Get historical price data for a symbol."""
    # Construct data directory path
    base_dir = "data/raw"
    symbol_dir = f"{base_dir}/{symbol.lower()}"
    
    if not os.path.exists(symbol_dir):
        return []
    
    # Find relevant data files
    data = []
    current_time = start_time
    while current_time <= end_time:
        # Construct path for this timestamp
        path = f"{symbol_dir}/{current_time.year}/{current_time.month:02d}/{current_time.day:02d}/{current_time.hour:02d}"
        if os.path.exists(path):
            # Read all files in this directory
            for filename in os.listdir(path):
                if not filename.endswith('.json'):
                    continue
                    
                file_time = datetime.strptime(filename.split('.')[0], "%Y%m%d_%H%M%S_%f")
                if start_time <= file_time <= end_time:
                    with open(os.path.join(path, filename), 'r') as f:
                        try:
                            file_data = json.load(f)
                            data.append(file_data)
                        except json.JSONDecodeError:
                            continue
                            
        current_time += timedelta(hours=1)
    
    return data

def get_analytics_data(symbol: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    """Get historical analytics data for a symbol."""
    # Similar to get_price_data but for analytics
    # For now, we'll calculate analytics from price data
    prices = get_price_data(symbol, start_time, end_time)
    if not prices:
        return []
        
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(prices)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample to 1-minute intervals and calculate analytics
    resampled = df.resample('1Min').agg({
        'price': ['mean', 'min', 'max']
    }).dropna()
    
    # Format results
    analytics = []
    for timestamp, row in resampled.iterrows():
        analytics.append({
            'symbol': symbol,
            'avg_price': row[('price', 'mean')],
            'min_price': row[('price', 'min')],
            'max_price': row[('price', 'max')],
            'timestamp': timestamp
        })
    
    return analytics

def get_alerts(symbol: Optional[str] = None, alert_type: Optional[str] = None,
               start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict]:
    """Get historical alerts."""
    # Read alerts from storage
    # For now, we'll return a sample alert
    return [{
        'type': 'threshold',
        'symbol': 'btcusdt',
        'price': 100000.0,
        'threshold': 100000.0,
        'direction': 'above',
        'timestamp': datetime.now()
    }]

# API routes
@app.get("/")
async def root():
    """API root endpoint."""
    return {"message": "Crypto Price API v1.0.0"}

@app.get("/prices/{symbol}", response_model=List[PriceData])
async def get_prices(
    symbol: str,
    start_time: datetime = Query(default=None),
    end_time: datetime = Query(default=None)
):
    """Get historical price data for a symbol."""
    # Default to last hour if no time range specified
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(hours=1)
        
    data = get_price_data(symbol, start_time, end_time)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
    return data

@app.get("/analytics/{symbol}", response_model=List[AnalyticsData])
async def get_analytics(
    symbol: str,
    start_time: datetime = Query(default=None),
    end_time: datetime = Query(default=None)
):
    """Get historical analytics data for a symbol."""
    # Default to last hour if no time range specified
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(hours=1)
        
    data = get_analytics_data(symbol, start_time, end_time)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
    return data

@app.get("/alerts", response_model=List[AlertData])
async def get_alert_history(
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get historical alerts."""
    alerts = get_alerts(symbol, alert_type, start_time, end_time)
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")
        
    return alerts

# WebSocket endpoint for real-time data
@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket):
    """Stream real-time price data."""
    await websocket.accept()
    
    try:
        # Initialize Kafka consumer
        consumer = KafkaConsumer(
            f'crypto_prices.{websocket.path_params["symbol"].lower()}',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )
        
        # Stream messages to WebSocket
        for message in consumer:
            await websocket.send_json(message.value)
            
    except Exception as e:
        await websocket.close()
    finally:
        consumer.close() 