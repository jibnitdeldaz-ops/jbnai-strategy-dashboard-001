import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def start_search_agent():
    print("🤖 Agent: Connecting to Google Search Network...")
    
    # We enable Google Search. This is the ultimate "Unblockable" tool.
    chat = client.chats.create(
        model="models/gemini-flash-latest",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            system_instruction="""
            ROLE: Senior Indian Financial Analyst.
            TASK: Search for the LATEST available closing price for the user's assets.
            FORMAT: Output a clean Markdown table with columns: [Asset Name] | [Price (INR)] | [Source].
            NOTE: If today is Sunday, explicitly mention these are Friday's closing prices.
            """
        )
    )

    # We list the exact search terms to ensure it finds the NSE tickers
    query = """
    Find the latest share price in Indian Rupees (INR) for these 11 assets on NSE/BSE:
    1. Bitcoin (BTC to INR)
    2. Nippon India ETF Gold BeES (GOLDBEES)
    3. Nippon India ETF Silver BeES (SILVERBEES)
    4. Nifty 50 Index
    5. Sensex Index
    6. HDFC Nifty Smallcap 250 ETF
    7. Nippon India ETF Junior BeES
    8. Motilal Oswal Nasdaq 100 ETF (MON100)
    9. Mirae Asset NYSE FANG+ ETF (MAFANG)
    10. Nippon India ETF Hang Seng BeES
    11. Mirae Asset Hang Seng Tech ETF (MAHKTECH)
    """
    
    print("📊 Searching live data (this may take 10-15 seconds)...")
    response = chat.send_message(query)
    
    print(f"\n{response.text}")
    
    # Print the sources so you know it's real
    if response.candidates[0].grounding_metadata:
        print("\n🔍 VERIFIED SOURCES:")
        for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
            if chunk.web:
                print(f"- {chunk.web.title}")

if __name__ == "__main__":
    start_search_agent()