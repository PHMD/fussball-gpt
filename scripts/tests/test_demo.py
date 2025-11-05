#!/usr/bin/env python3
"""Quick test of KSI demo"""

import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

TEST_QUERY = "Wer führt die Bundesliga-Tabelle an?"

BUNDESLIGA_DATA = "Tabelle: 1. Bayer Leverkusen - 25 Punkte, 2. Bayern München - 23 Punkte"

SYSTEM_PROMPT = "Du bist ein deutscher Sportjournalist. Antworte kurz und präzise auf Deutsch."

print(f"Testing Mistral Large with: {TEST_QUERY}")
print("Querying...")

try:
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{BUNDESLIGA_DATA}"},
            {"role": "user", "content": TEST_QUERY}
        ],
        max_tokens=500
    )

    answer = response.choices[0].message.content
    print(f"\n✅ Success!\n\nResponse: {answer}\n")

except Exception as e:
    print(f"\n❌ Error: {str(e)}\n")
