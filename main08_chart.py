import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. ASSETS
ASSETS = {
    "Nifty 50": "^NSEI",
    "Bitcoin": "BTC-USD",
    "Gold BeES": "GOLDBEES.NS",
    "Silver BeES": "SILVERBEES.NS",
    "Junior BeES": "JUNIORBEES.NS",
    "Smallcap 250": "HDFCSML250.NS",
    "MON100": "MON100.NS",
    "MAFANG": "MAFANG.NS",
    "HangSeng BeES": "HNGSNGBEES.NS",
    "MAHKTECH": "MAHKTECH.NS",
    "Sensex": "^BSESN"
}

# 2. RSI MATH
def calculate_rsi(series, period=2):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.ewm(min_periods=period, adjust=False, alpha=1/period).mean()
    avg_loss = loss.ewm(min_periods=period, adjust=False, alpha=1/period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def create_pro_chart(name, ticker):
    print(f"📊 Processing {name}...")
    try:
        # DOWNLOAD
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if df.empty:
            print(f"   ⚠️ No data for {ticker}")
            return None

        # --- CRITICAL FIX: FLATTEN COLUMNS ---
        # If columns look like ('Close', 'BTC-USD'), we want just 'Close'
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # --- CRITICAL FIX: NUKE TIMEZONES ---
        # We convert everything to "Naive" time (no timezone) to stop the crash
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        # RESAMPLE TO WEEKLY
        # Now that columns are flat ('Open', 'Close'), this will work:
        df_weekly = df.resample('W-FRI').agg({
            'Open': 'first', 
            'High': 'max', 
            'Low': 'min', 
            'Close': 'last'
        }).dropna()

        # Indicators
        df_weekly['RSI_2'] = calculate_rsi(df_weekly['Close'], period=2)
        df_weekly['MA_90'] = df_weekly['Close'].rolling(window=13).mean()

        # Plotting
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3],
                            subplot_titles=(f"{name}", "RSI(2)"))

        # Candle
        fig.add_trace(go.Candlestick(
            x=df_weekly.index, open=df_weekly['Open'], high=df_weekly['High'],
            low=df_weekly['Low'], close=df_weekly['Close'], name="Price"
        ), row=1, col=1)

        # 90 MA
        fig.add_trace(go.Scatter(
            x=df_weekly.index, y=df_weekly['MA_90'], line=dict(color='yellow', width=2), name="90MA"
        ), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=df_weekly.index, y=df_weekly['RSI_2'], line=dict(color='#ab47bc', width=2), name="RSI"
        ), row=2, col=1)

        # Zones
        fig.add_hrect(y0=0, y1=20, fillcolor="green", opacity=0.1, line_width=0, row=2, col=1)
        fig.add_hline(y=10, line_dash="dot", line_color="green", row=2, col=1)

        fig.update_layout(template="plotly_dark", height=500, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
        fig.update_xaxes(rangeslider_visible=False)

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def build_dashboard():
    print("🚀 Starting Engine...")
    html_content = "<html><head><title>My Charts</title><style>body{background:#111;color:white;font-family:sans-serif;}</style></head><body><h1 style='text-align:center;color:#00e676'>RSI(2) Mean Reversion Dashboard</h1>"
    
    for name, ticker in ASSETS.items():
        chart = create_pro_chart(name, ticker)
        if chart:
            html_content += f"<div style='border:1px solid #333; margin:20px; padding:10px;'>{chart}</div>"
    
    html_content += "</body></html>"
    with open("my_pro_charts.html", "w") as f:
        f.write(html_content)
    print("\n✅ Done. Open 'my_pro_charts.html'")

if __name__ == "__main__":
    build_dashboard()