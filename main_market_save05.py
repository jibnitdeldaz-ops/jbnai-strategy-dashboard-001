import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load the PAID Key
load_dotenv(override=True)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Auto-Discovery (Finds the best model your $300 credit unlocks)
def get_best_available_model():
    try:
        all_models = list(client.models.list())
        for m in all_models:
            # We look for the newest stable flash model
            if "flash" in m.name and "legacy" not in m.name and "8b" not in m.name:
                return m.name
        return "models/gemini-2.0-flash" # Fallback
    except:
        return "models/gemini-2.0-flash-lite"

# 3. The Save Tool
def save_report_to_disk(filename: str, content: str) -> str:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ SUCCESS: Full Report saved to {filename}"
    except Exception as e:
        return f"❌ ERROR: {e}"

def start_full_portfolio_agent():
    best_model = get_best_available_model()
    print(f"🤖 Agent: Connected via {best_model}")
    print("📊 Status: Fetching data for all 11 Assets...")

    # The list is back!
    portfolio_query = """
    I need a table of the latest prices (INR) for these 11 assets.
    If the market is closed (Sunday), give me the Friday closing price.
    
    1. Bitcoin (BTC) - Live Price
    2. Nippon Gold BeES ETF
    3. Nippon Silver BeES ETF
    4. Nifty 50 Index
    5. Sensex Index
    6. HDFC Nifty Smallcap 250 ETF
    7. Nippon Junior BeES ETF
    8. Motilal Oswal Nasdaq 100 ETF (MON100)
    9. Mirae Asset NYSE FANG+ ETF (MAFANG)
    10. Nippon HangSeng BeES ETF
    11. Mirae Asset Hang Seng Tech ETF (MAHKTECH)

    Format: Markdown Table [Asset | Price (INR) | Date/Status]
    """

    try:
        response = client.models.generate_content(
            model=best_model, 
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction="You are a Senior Investment Analyst. precision is key."
            ),
            contents=portfolio_query
        )
        
        report_data = response.text
        print("\n✅ Analysis Complete. Saving to disk...")
        
        # Python saves the file
        result = save_report_to_disk("portfolio_report.md", report_data)
        
        print(result)
        print("------------------------------------------------")
        print(report_data) # Print to terminal for verification

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    start_full_portfolio_agent()