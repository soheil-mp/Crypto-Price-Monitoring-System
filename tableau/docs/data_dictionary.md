# Crypto Analytics Data Dictionary

## Price Data Files
Files: `crypto_prices_*.csv`, `realtime_prices_*.csv`

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timestamp | datetime | Time of price update | 2024-01-10T14:30:00Z |
| symbol | string | Trading pair | BTCUSDT |
| price | float | Current price | 45123.45 |
| volume | float | Trading volume | 123.45 |
| exchange | string | Source exchange | binance |
| date | date | Extracted date | 2024-01-10 |
| year | integer | Year | 2024 |
| month | integer | Month number | 1 |
| month_name | string | Month name | January |
| day | integer | Day of month | 10 |
| hour | integer | Hour (24h) | 14 |
| minute | integer | Minute | 30 |
| day_of_week | string | Day name | Wednesday |
| week_of_year | integer | ISO week number | 2 |
| is_weekend | boolean | Weekend flag | false |
| trading_session | string | Trading period | Afternoon |

## Technical Indicators
Files: `crypto_prices_*.csv`

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| ma_5min | float | 5-minute Moving Average | 45120.34 |
| ma_15min | float | 15-minute Moving Average | 45118.67 |
| ma_1hour | float | 1-hour Moving Average | 45115.89 |
| ema_5min | float | 5-minute Exponential MA | 45121.23 |
| ema_15min | float | 15-minute Exponential MA | 45119.45 |
| ema_1hour | float | 1-hour Exponential MA | 45116.78 |
| bb_middle | float | Bollinger Band Middle | 45120.00 |
| bb_upper | float | Bollinger Band Upper | 45220.00 |
| bb_lower | float | Bollinger Band Lower | 45020.00 |
| bb_width | float | Bollinger Band Width | 0.0044 |
| macd | float | MACD Line | 12.34 |
| macd_signal | float | MACD Signal Line | 11.22 |
| macd_histogram | float | MACD Histogram | 1.12 |
| stoch_k | float | Stochastic %K | 75.5 |
| stoch_d | float | Stochastic %D | 72.3 |
| atr | float | Average True Range | 123.45 |
| rsi | float | Relative Strength Index | 65.4 |

## Analytics Data
Files: `crypto_analytics_*.csv`, `realtime_analytics_*.csv`

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timestamp | datetime | Analysis timestamp | 2024-01-10T14:30:00Z |
| symbol | string | Trading pair | BTCUSDT |
| min_price | float | Period minimum price | 44800.00 |
| max_price | float | Period maximum price | 45300.00 |
| avg_price | float | Period average price | 45100.00 |
| price_range | float | Price range (max-min) | 500.00 |
| price_volatility | float | Volatility measure | 0.0111 |
| volatility_level | string | Categorized volatility | Medium |
| market_trend | string | Overall trend | Uptrend |

## Alert Data
Files: `realtime_alerts_*.csv`

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timestamp | datetime | Alert timestamp | 2024-01-10T14:30:00Z |
| symbol | string | Trading pair | BTCUSDT |
| alert_type | string | Type of alert | Price Spike |
| severity | string | Alert severity | High |
| message | string | Alert description | "5% price increase in 5 minutes" |

## Update Frequencies

| Data Type | Update Frequency | Retention |
|-----------|-----------------|-----------|
| Price Data | 5 seconds | 24 hours |
| Analytics | 15 seconds | 24 hours |
| Alerts | Real-time | 1 hour |
| Technical Indicators | 5 seconds | 24 hours |

## Notes
- All timestamps are in UTC
- Price data is sourced from major exchanges
- Technical indicators are calculated in real-time
- Data is automatically cleaned after retention period 