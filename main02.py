import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# THE BOSS MOVE: Persona + Self-Correction + Few-Shot Examples
SYSTEM_PROMPT = """
ROLE: Cyber-Security Analyst.
FORMAT: Use a structured [SUMMARY] block followed by a [DETAILED_ANALYSIS].

EXAMPLES:
Input: "What is SQL Injection?"
Output: 
[SUMMARY]
- Risk Level: CRITICAL
- Category: Injection Attack
- Impact: Database Takeover
[DETAILED_ANALYSIS]
SQL Injection (SQLi) occurs when... (etc)

Input: "Is 2FA secure?"
Output:
[SUMMARY]
- Risk Level: LOW (Mitigated)
- Category: Authentication
- Impact: Account Takeover prevention
[DETAILED_ANALYSIS]
While highly effective, 2FA can be bypassed via... (etc)
"""

def start_few_shot_agent():
    print("🤖 Agent: Learning from examples...")
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
            # New query for the agent to analyze using your examples
            contents="Explain the risks of using outdated NPM packages."
        )
        print(f"\n{response.text}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    start_few_shot_agent()