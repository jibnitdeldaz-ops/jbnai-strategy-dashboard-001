import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
# Using the production client we established yesterday
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def start_grounded_agent():
    print("🌐 Agent: Connecting to Google Search...")
    try:
        # THE BOSS MOVE: Adding the Google Search Tool
        response = client.models.generate_content(
            model="models/gemini-flash-latest", 
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
            # Ask about something that happened RECENTLY in 2026
            contents="What are the top three cyber-security breaches reported in January 2026?"
        )
        
        print(f"\n{response.text}")
        
        # Check for citations (The "Grounding" proof)
        if response.candidates[0].grounding_metadata:
            print("\n🔍 SOURCE DATA:")
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                if chunk.web:
                    print(f"- {chunk.web.title}: {chunk.web.uri}")

        print("\n🚀 DAY 4 MISSION SUCCESSFUL: Agent is now live-linked.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    start_grounded_agent()