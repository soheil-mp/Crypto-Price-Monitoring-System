"""Chart components for the Streamlit app."""

import plotly.graph_objects as go
from src.visualization.streamlit.config.constants import COLORS

def create_price_chart(df, indicators, selected_crypto, scale_type='Linear'):
    """Create the main price chart with technical indicators."""
    # Calculate y-axis range with padding
    min_price = df['price'].min()
    max_price = df['price'].max()
    price_range = max_price - min_price
    
    # Add padding to make variations more visible
    if price_range < 0.01:  # Very small range
        padding = price_range * 2
    elif price_range < 0.1:  # Small range
        padding = price_range
    else:
        padding = price_range * 0.1  # Normal range
    
    y_min = min_price - padding
    y_max = max_price + padding

    fig = go.Figure()

    # Add price line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            name='Price',
            line=dict(
                color=COLORS['primary'],
                width=3,
            ),
            fill='tonexty',
            fillcolor='rgba(0, 255, 242, 0.05)',
            hovertemplate="<b>Price:</b> $%{y:,.4f}<br><b>Time:</b> %{x}<extra></extra>"
        )
    )

    # Add technical indicators
    if indicators.get('sma'):
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df[f'SMA_{indicators["sma_period"]}'],
                name=f'SMA {indicators["sma_period"]}',
                line=dict(
                    color='rgba(255, 42, 255, 0.8)',
                    width=2,
                    dash='dash',
                ),
                hovertemplate=f"<b>SMA {indicators['sma_period']}:</b> $%{{y:,.4f}}<extra></extra>"
            )
        )

    if indicators.get('ema'):
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df[f'EMA_{indicators["ema_period"]}'],
                name=f'EMA {indicators["ema_period"]}',
                line=dict(
                    color='rgba(0, 255, 157, 0.8)',
                    width=2,
                    dash='dot',
                ),
                hovertemplate=f"<b>EMA {indicators['ema_period']}:</b> $%{{y:,.4f}}<extra></extra>"
            )
        )

    if indicators.get('bb'):
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['BB_upper'],
                name='BB Upper',
                line=dict(
                    color='rgba(255, 27, 107, 0.8)',
                    width=1.5,
                ),
                hovertemplate="<b>BB Upper:</b> $%{y:,.4f}<extra></extra>"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['BB_lower'],
                name='BB Lower',
                line=dict(
                    color='rgba(255, 27, 107, 0.8)',
                    width=1.5,
                ),
                fill='tonexty',
                fillcolor='rgba(255, 27, 107, 0.05)',
                hovertemplate="<b>BB Lower:</b> $%{y:,.4f}<extra></extra>"
            )
        )

    # Enhanced chart layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f'{selected_crypto} Price Chart',
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color=COLORS['text'],
                family='Inter'
            )
        ),
        xaxis=dict(
            title='Time',
            showgrid=True,
            gridwidth=0.3,
            gridcolor=COLORS['grid'],
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            title='Price (USD)',
            showgrid=True,
            gridwidth=0.3,
            gridcolor=COLORS['grid'],
            tickformat='$,.4f',
            side='right',
            range=[y_min, y_max],
            type='log' if scale_type == 'Logarithmic' else 'linear',
            dtick=0.5 if scale_type == 'Logarithmic' else None,
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor=COLORS['border'],
            borderwidth=1,
            font=dict(
                color=COLORS['text'],
                size=12
            ),
            x=0,
            y=1,
            yanchor='bottom'
        ),
        height=600,
        margin=dict(t=80, b=40, l=40, r=40),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(10, 13, 28, 0.9)',
            font=dict(
                size=12,
                color=COLORS['text'],
                family='Inter'
            ),
            bordercolor=COLORS['border']
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color=COLORS['text_secondary'],
            activecolor=COLORS['primary']
        )
    )

    # Add range selector
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1H", step="hour", stepmode="backward"),
                dict(count=4, label="4H", step="hour", stepmode="backward"),
                dict(count=12, label="12H", step="hour", stepmode="backward"),
                dict(count=24, label="24H", step="hour", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor=COLORS['card_bg'],
            activecolor=COLORS['primary'],
            font=dict(color=COLORS['text'])
        )
    )

    return fig

def create_rsi_chart(df, rsi_period):
    """Create the RSI chart."""
    fig = go.Figure()
    
    # Add RSI line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['RSI'],
            name='RSI',
            line=dict(color='#DDA0DD', width=2),
            hovertemplate="<b>RSI:</b> %{y:.2f}<extra></extra>"
        )
    )

    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5,
                  annotation_text="Overbought", annotation_position="right")
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5,
                  annotation_text="Oversold", annotation_position="right")

    # Update layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f'RSI ({rsi_period})',
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        height=250,
        yaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)',
            side='right'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(t=50, b=20),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font_size=12
        )
    )
    
    return fig

def create_macd_chart(df):
    """Create the MACD chart."""
    fig = go.Figure()
    
    # Add MACD line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['MACD'],
            name='MACD',
            line=dict(color='#00B5F0', width=2),
            hovertemplate="<b>MACD:</b> %{y:.2f}<extra></extra>"
        )
    )
    
    # Add Signal line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['Signal_Line'],
            name='Signal',
            line=dict(color='#FF4444', width=2),
            hovertemplate="<b>Signal:</b> %{y:.2f}<extra></extra>"
        )
    )
    
    # Add Histogram
    colors = ['#00FF00' if val >= 0 else '#FF4444' for val in df['MACD_Histogram']]
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.5,
            hovertemplate="<b>Histogram:</b> %{y:.2f}<extra></extra>"
        )
    )

    # Update layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='MACD (12, 26, 9)',
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        height=250,
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.2)',
            side='right'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(t=50, b=20),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font_size=12
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_volume_chart(df, selected_crypto):
    """Create the volume chart."""
    fig = go.Figure()
    
    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volume_24h'],
            name='Volume',
            marker_color='rgba(0, 181, 240, 0.5)',
            hovertemplate="<b>Volume:</b> $%{y:,.0f}<extra></extra>"
        )
    )

    # Update layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f'{selected_crypto} Trading Volume',
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        height=250,
        yaxis=dict(
            title='Volume (USD)',
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)',
            tickformat=',',
            side='right'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(t=50, b=20),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font_size=12
        )
    )
    
    return fig 