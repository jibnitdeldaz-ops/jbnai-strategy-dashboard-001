import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# STEP 1: Define the actual Python function
def calculate_risk_score(breach_count: int, industry_multiplier: float) -> dict:
    """Calculates a security risk score based on history and industry type."""
    # This logic happens locally on your machine, not in the AI cloud
    score = (breach_count * 10) * industry_multiplier
    return {"risk_score": score, "level": "HIGH" if score > 50 else "LOW"}

# STEP 2: Declare the tool for the AI
# In the 2026 SDK, we can pass functions directly!
tools_list = [calculate_risk_score]

def start_agent_with_hands():
    print("🤖 Agent: Initializing with Custom Calculation Tool...")
    
    # We use a chat session because it handles the back-and-forth of tools automatically
    chat = client.chats.create(
        model="models/gemini-flash-latest",
        config=types.GenerateContentConfig(tools=tools_list)
    )

    #prompt = "I'm a Fintech company with 3 recent breaches. What is my risk score?"
    prompt = "I'm a Fintech company with 3 breaches. Use a multiplier of 2.5. What is my score?"
    
    # The 'google-genai' SDK handles the function calling loop for you!
    response = chat.send_message(prompt)
    
    print(f"\nAI RESPONSE: {response.text}")
    print("\n🚀 DAY 5 MISSION SUCCESSFUL: Tool executed.")

if __name__ == "__main__":
    start_agent_with_hands()