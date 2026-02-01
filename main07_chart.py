import os
from dotenv import load_dotenv

# We don't even need the GenAI library for the GUI generation part! 
# This saves your quota for the 'Strategy Advice' later.

TV_CONFIGS = {
    "Bitcoin": "BINANCE:BTCUSDT",
    "Nifty 50": "NSE:NIFTY",
    "Sensex": "BSE:SENSEX",
    "Gold BeES": "NSE:GOLDBEES",
    "Silver BeES": "NSE:SILVERBEES",
    "Smallcap 250": "NSE:HDFCSML250",
    "Junior BeES": "NSE:JUNIORBEES",
    "MON100": "NSE:MON100",
    "MAFANG": "NSE:MAFANG",
    "HangSeng BeES": "NSE:HNGSNGBEES",
    "MAHKTECH": "NSE:MAHKTECH"
}

def build_god_mode_gui():
    print("🎨 Building High-Performance Dashboard...")
    
    html_start = """
    <html>
    <head>
        <title>Mean Reversion Pro</title>
        <style>
            body { background: #131722; color: white; font-family: sans-serif; margin: 0; padding: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(500px, 1fr)); gap: 15px; }
            .card { background: #1e222d; border-radius: 12px; padding: 10px; border: 1px solid #363c4e; height: 500px; }
            h2 { margin: 5px 0; color: #2962ff; font-size: 18px; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">📉 RSI(2) & 90MA STRATEGY COMMAND CENTER</h1>
        <div class="grid">
    """

    cards = ""
    for name, symbol in TV_CONFIGS.items():
        # WE INJECT THE RSI AND MA DIRECTLY INTO THE WIDGET
        cards += f"""
        <div class="card">
            <h2>{name} ({symbol})</h2>
            <div id="widget_{name.replace(' ', '')}" style="height:450px;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
              "width": "100%",
              "height": 450,
              "symbol": "{symbol}",
              "interval": "W",
              "timezone": "Asia/Kolkata",
              "theme": "dark",
              "style": "1",
              "locale": "en",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "hide_top_toolbar": false,
              "hide_legend": false,
              "save_image": false,
              "container_id": "widget_{name.replace(' ', '')}",
              "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies"
              ],
              "show_popup_button": true,
              "popup_width": "1000",
              "popup_height": "650"
            }});
            </script>
        </div>
        """

    html_end = "</div></body></html>"
    
    with open("hero_dashboard.html", "w") as f:
        f.write(html_start + cards + html_end)
    
    print("\n✅ DASHBOARD READY: Open 'hero_dashboard.html'")
    print("👉 Pro Tip: Once open, click the Gear Icon on RSI to change length to 2.")

if __name__ == "__main__":
    build_god_mode_gui()