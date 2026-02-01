import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

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

# 2. INDICATORS
def calculate_indicators(df):
    # RSI (2)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.ewm(min_periods=2, adjust=False, alpha=1/2).mean()
    avg_loss = loss.ewm(min_periods=2, adjust=False, alpha=1/2).mean()
    rs = avg_gain / avg_loss
    df['RSI_2'] = 100 - (100 / (1 + rs))

    # 90-Day MA (approx 13 weeks)
    df['MA_90'] = df['Close'].rolling(window=13).mean()

    # UT Bot (ATR Trailing Stop)
    h_l = df['High'] - df['Low']
    h_pc = abs(df['High'] - df['Close'].shift(1))
    l_pc = abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    atr = tr.rolling(10).mean()
    df['UT_Stop'] = df['Close'] - (atr * 2) 
    
    return df

def get_signal(row):
    rsi = row['RSI_2']
    price = row['Close']
    ut_stop = row['UT_Stop']
    
    if rsi < 10: return "⚡ AGGRESSIVE ADD", "#00e676"
    elif rsi < 20: return "🟢 BUY / ACCUMULATE", "#66bb6a"
    elif rsi > 90: return "🔴 BOOK PROFIT", "#ff1744"
    elif price < ut_stop: return "⚠️ DOWNTREND", "#ffa726"
    else: return "⚪ WAIT / HOLD", "#78909c"

def create_card(name, ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        if df.index.tz is not None: df.index = df.index.tz_localize(None)

        df_weekly = df.resample('W-FRI').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
        df_weekly = calculate_indicators(df_weekly)
        last_row = df_weekly.iloc[-1]
        sig_text, sig_color = get_signal(last_row)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
        fig.add_trace(go.Candlestick(x=df_weekly.index, open=df_weekly['Open'], high=df_weekly['High'], low=df_weekly['Low'], close=df_weekly['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_weekly.index, y=df_weekly['MA_90'], line=dict(color='#ffea00', width=2), name="90MA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_weekly.index, y=df_weekly['UT_Stop'], line=dict(color='#2979ff', dash='dot'), name="UT Bot"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_weekly.index, y=df_weekly['RSI_2'], line=dict(color='#ab47bc', width=2), name="RSI"), row=2, col=1)
        fig.add_hrect(y0=0, y1=20, fillcolor="green", opacity=0.1, line_width=0, row=2, col=1)
        fig.add_hrect(y0=90, y1=100, fillcolor="red", opacity=0.1, line_width=0, row=2, col=1)
        fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), height=400, showlegend=False, paper_bgcolor="#1e222d", plot_bgcolor="#1e222d")
        fig.update_xaxes(rangeslider_visible=False)
        
        return f"""
        <div class="card" style="border-top: 4px solid {sig_color};">
            <div class="header"><h3>{name}</h3><span class="badge" style="background:{sig_color}20; color:{sig_color}">{sig_text}</span></div>
            <div class="stats"><span>RSI(2): <strong style="color:#fff">{last_row['RSI_2']:.1f}</strong></span><span>Price: <strong style="color:#fff">{last_row['Close']:.1f}</strong></span></div>
            {fig.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>"""
    except: return None

if __name__ == "__main__":
    print("🚀 Updating Dashboard...")
    cards = ""
    for n, t in ASSETS.items():
        c = create_card(n, t)
        if c: cards += c
    
    html = f"""
    <!DOCTYPE html><html><head><title>Strategy Dashboard</title><meta charset="utf-8">
    <style>body{{background:#131722;color:#d1d4dc;font-family:sans-serif;padding:20px;}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px;}} .card{{background:#1e222d;padding:15px;border-radius:8px;}} .header{{display:flex;justify-content:space-between;margin-bottom:10px;}} .badge{{padding:4px 8px;border-radius:4px;font-weight:bold;}} .stats{{color:#888;margin-bottom:10px;display:flex;gap:15px;}}</style>
    </head><body><h1 style="text-align:center;color:#2962ff">⚡ RSI(2) + UT BOT DASHBOARD</h1><div class="grid">{cards}</div>
    <p style="text-align:center;color:#555;margin-top:20px">Auto-updated by GitHub Actions</p></body></html>
    """
    
    # OUTPUTS TO index.html (Standard Webpage Name)
    with open("index.html", "w") as f:
        f.write(html)
    print("✅ Done: index.html updated.")