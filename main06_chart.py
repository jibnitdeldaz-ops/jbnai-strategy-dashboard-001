import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Mapping your Indian ETFs to TradingView-compatible symbols
TV_SYMBOLS = {
    "Bitcoin": "BINANCE:BTCUSDT",
    "Gold BeES": "NSE:GOLDBEES",
    "Silver BeES": "NSE:SILVERBEES",
    "Nifty 50": "NSE:NIFTY",
    "Sensex": "BSE:SENSEX",
    "Smallcap 250": "NSE:HDFCSML250",
    "Junior BeES": "NSE:JUNIORBEES",
    "MON100": "NSE:MON100",
    "MAFANG": "NSE:MAFANG",
    "HangSeng BeES": "NSE:HNGSNGBEES",
    "MAHKTECH": "NSE:MAHKTECH"
}

def generate_dashboard():
    print("🧠 Step 1: Getting AI Market Sentiment (Indices Only)...")
    
    # We only search for the main Index to avoid hitting the 429 limit
    query = "Quick status of Nifty 50 and Bitcoin vs their 90-day Moving Average. Are we in a 'Dead Rubber' or 'Overheated' zone?"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction="Keep it brief (3 sentences)."
            ),
            contents=query
        )
        ai_intel = response.text
    except:
        ai_intel = "Market Data Hub Active. View charts below for RSI(2) signals."

    print("🎨 Step 2: Generating Strategy GUI...")
    
    html_start = f"""
    <html>
    <head>
        <title>RSI(2) Mean Reversion Dashboard</title>
        <style>
            body {{ background: #131722; color: white; font-family: sans-serif; padding: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 15px; }}
            .card {{ background: #1e222d; border-radius: 10px; padding: 10px; border: 1px solid #363c4e; }}
            .header {{ background: #2962ff; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Strategy Dashboard: RSI(2) + 90MA</h1>
            <p><strong>AI Intel:</strong> {ai_intel}</p>
        </div>
        <div class="grid">
    """
    
    cards = ""
    for name, symbol in TV_SYMBOLS.items():
        cards += f"""
        <div class="card">
            <h3 style="margin:5px;">{name}</h3>
            <div id="tv_{name.replace(' ', '')}" style="height:350px;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
              "width": "100%", "height": 350, "symbol": "{symbol}",
              "interval": "W", "timezone": "Asia/Kolkata", "theme": "dark",
              "style": "1", "locale": "en", "enable_publishing": false,
              "hide_top_toolbar": true, "hide_legend": true,
              "container_id": "tv_{name.replace(' ', '')}"
            }});
            </script>
        </div>
        """

    with open("full_strategy_gui.html", "w") as f:
        f.write(html_start + cards + "</div></body></html>")
    
    print("\n✅ SUCCESS: GUI Generated as 'full_strategy_gui.html'.")

if __name__ == "__main__":
    generate_dashboard()