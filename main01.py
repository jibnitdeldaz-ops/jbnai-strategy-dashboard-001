import os
from dotenv import load_dotenv
from google import genai
from google.genai import types # New import for config

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# THE BOSS MOVE: Defining the System Persona
SYSTEM_PROMPT = """
ROLE: You are a Cyber-Security Research Agent specializing in 2026 threat landscapes.
MISSION: Analyze user queries for security risks and provide technical summaries.

SELF-CORRECTION RULES:
1. After generating your initial draft, review it for technical accuracy.
2. Ensure all 2026-specific claims are logically sound.
3. If the draft contains generic advice (e.g., 'use strong passwords'), replace it with advanced technical mitigations.
4. ONLY output the final, polished version. Do not show your "thinking" unless asked.
"""

def start_research_agent():
    print("🤖 Agent Persona: 'Security Analyst' Initialized...")
    try:
        # We pass the persona into the 'config' parameter
        response = client.models.generate_content(
            model="models/gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
            contents="How can a company protect its API keys in a public GitHub repo?"
        )
        
        print(f"\n{response.text}")
        print("\n🚀 DAY 2 MISSION SUCCESSFUL: Persona active.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    start_research_agent()