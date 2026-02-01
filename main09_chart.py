print("🟢 DEBUG: Script Initialized. Importing libraries...") # DEBUG LINE

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. ASSETS CONFIGURATION
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

# 2. MATH ENGINE (RSI + UT BOT)
def calculate_indicators(df):
    # --- RSI (2) Calculation ---
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.ewm(min_periods=2, adjust=False, alpha=1/2).mean()
    avg_loss = loss.ewm(min_periods=2, adjust=False, alpha=1/2).mean()
    rs = avg_gain / avg_loss
    df['RSI_2'] = 100 - (100 / (1 + rs))

    # --- 90-Day Moving Average ---
    # We use 13 weeks to approximate 90 days (13 * 7 = 91 days)
    df['MA_90'] = df['Close'].rolling(window=13).mean()

    # --- UT BOT (ATR Trailing Stop) ---
    # 1. True Range
    h_l = df['High'] - df['Low']
    h_pc = abs(df['High'] - df['Close'].shift(1))
    l_pc = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    
    # 2. ATR (10 Period)
    atr = tr.rolling(10).mean()
    
    # 3. Trailing Stop (Sensitivity = 2)
    # If price is below this line, UT Bot says "SELL/DOWNTREND"
    df['UT_Stop'] = df['Close'] - (atr * 2) 
    
    return df

def get_strategy_signal(row):
    rsi = row['RSI_2']
    price = row['Close']
    ut_stop = row['UT_Stop']
    
    # --- YOUR STRATEGY RULES ---
    
    # Rule 1: Crash Buying (RSI < 10)
    if rsi < 10:
        return "⚡ AGGRESSIVE ADD", "#00e676" # Bright Green
    
    # Rule 2: Dip Buying (RSI < 20)
    elif rsi < 20:
        return "🟢 BUY / ACCUMULATE", "#66bb6a" # Medium Green
        
    # Rule 3: Profit Booking (RSI > 90)
    elif rsi > 90:
        return "🔴 BOOK PROFIT", "#ff1744" # Red
        
    # Rule 4: Trend Check (UT Bot)
    # If Price is significantly below the ATR stop, it's a downtrend
    # We use a simple check: is price < UT Stop?
    elif price < ut_stop:
         return "⚠️ UT BOT: DOWNTREND", "#ffa726" # Orange
         
    else:
        return "⚪ WAIT / HOLD", "#78909c" # Grey

def create_chart_card(name, ticker):
    print(f"📊 Analyzing {name}...")
    try:
        # Fetch Data (No Progress Bar to keep terminal clean)
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if df.empty: 
            print(f"   ⚠️ No data for {name}")
            return None
        
        # Cleanup: Flatten columns if MultiIndex (Fixes the 'Label' error)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
            
        # Cleanup: Remove Timezone (Fixes the 'ZoneInfo' error)
        if df.index.tz is not None: 
            df.index = df.index.tz_localize(None)

        # Resample to Weekly (Friday Close)
        df_weekly = df.resample('W-FRI').agg({
            'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'
        }).dropna()

        # Add Indicators
        df_weekly = calculate_indicators(df_weekly)
        
        # Get Latest Signal from the very last week
        last_row = df_weekly.iloc[-1]
        signal_text, signal_color = get_strategy_signal(last_row)

        # --- PLOTTING (Plotly) ---
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.75, 0.25]
        )

        # 1. Price Candle
        fig.add_trace(go.Candlestick(
            x=df_weekly.index, open=df_weekly['Open'], high=df_weekly['High'],
            low=df_weekly['Low'], close=df_weekly['Close'], name="Price"
        ), row=1, col=1)

        # 2. 90 MA (Yellow Line)
        fig.add_trace(go.Scatter(
            x=df_weekly.index, y=df_weekly['MA_90'], 
            line=dict(color='#ffea00', width=2), name="90MA"
        ), row=1, col=1)

        # 3. UT Bot Stop Line (Blue Dashed)
        fig.add_trace(go.Scatter(
            x=df_weekly.index, y=df_weekly['UT_Stop'], 
            line=dict(color='#2979ff', dash='dot'), name="UT Bot"
        ), row=1, col=1)

        # 4. RSI Panel (Bottom)
        fig.add_trace(go.Scatter(
            x=df_weekly.index, y=df_weekly['RSI_2'], 
            line=dict(color='#ab47bc', width=2), name="RSI(2)"
        ), row=2, col=1)
        
        # RSI Zones (Green < 20, Red > 90)
        fig.add_hrect(y0=0, y1=20, fillcolor="green", opacity=0.1, line_width=0, row=2, col=1)
        fig.add_hrect(y0=90, y1=100, fillcolor="red", opacity=0.1, line_width=0, row=2, col=1)
        fig.add_hline(y=10, line_dash="dot", line_color="#00e676", row=2, col=1)

        # Chart Styling
        fig.update_layout(
            template="plotly_dark", 
            margin=dict(l=0, r=0, t=0, b=0),
            height=400, 
            showlegend=False,
            paper_bgcolor="#1e222d",
            plot_bgcolor="#1e222d"
        )
        fig.update_xaxes(rangeslider_visible=False)

        # Generate HTML fragment
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # Create the Card HTML
        return f"""
        <div class="card" style="border-top: 4px solid {signal_color};">
            <div class="header">
                <h3>{name}</h3>
                <span class="badge" style="background:{signal_color}20; color:{signal_color}">{signal_text}</span>
            </div>
            <div class="stats">
                <span>RSI(2): <strong style="color:#fff">{last_row['RSI_2']:.1f}</strong></span>
                <span>Price: <strong style="color:#fff">{last_row['Close']:.1f}</strong></span>
            </div>
            {chart_html}
        </div>
        """

    except Exception as e:
        print(f"❌ Error analyzing {name}: {e}")
        return None

def build_dashboard():
    print("🚀 Starting Dashboard Engine...")
    print("🎨 Formatting: Grid Layout + UT Bot + RSI Strategy")
    
    html_start = """
    <!DOCTYPE html>
    <html><head><title>Strategy Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { background: #131722; color: #d1d4dc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; margin: 0; }
        h1 { text-align:center; color:#2962ff; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; }
        .card { background: #1e222d; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        h3 { margin: 0; color: #fff; font-size: 18px; }
        .badge { padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid; }
        .stats { display: flex; gap: 20px; font-size: 14px; color: #888; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #2a2e39; }
    </style>
    </head><body>
    <h1>⚡ RSI(2) + UT BOT DASHBOARD</h1>
    <div class="grid">
    """
    
    cards_html = ""
    for name, ticker in ASSETS.items():
        card = create_chart_card(name, ticker)
        if card: cards_html += card
            
    with open("strategy_dashboard.html", "w") as f:
        f.write(html_start + cards_html + "</div></body></html>")
    
    print("\n✅ SUCCESS: Open 'strategy_dashboard.html' to see the GRID.")

# --- THE START BUTTON (Crucial!) ---
if __name__ == "__main__":
    build_dashboard()