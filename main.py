import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def start_mission():
    print("🤖 System Check: Engaging 'gemini-flash-latest'...")
    try:
        # We use the ALIAS found in your list. 
        # This routes to the stable, quota-enabled version automatically.
        response = client.models.generate_content(
            model="models/gemini-flash-latest", 
            contents="Confirm system online in 5 words."
        )
        
        print(f"\nAI RESPONSE: {response.text}")
        print("🚀 DAY 1 MISSION SUCCESSFUL!")
        print("Route: Alias (gemini-flash-latest) | Status: ONLINE\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        # If Flash fails, we try the Pro alias as a backup
        if "429" in str(e) or "404" in str(e):
             print("⚠️ Flash failed. Trying 'models/gemini-pro-latest'...")
             try:
                 response = client.models.generate_content(
                    model="models/gemini-pro-latest", 
                    contents="Confirm system online."
                 )
                 print(f"AI RESPONSE: {response.text}")
             except Exception as e2:
                 print(f"❌ Backup failed: {e2}")

if __name__ == "__main__":
    start_mission()