#!/usr/bin/env python3
"""Quick test of KSI bilingual demo"""

import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

TEST_QUERY_DE = "Wer führt die Bundesliga-Tabelle an?"
TEST_QUERY_EN = "Who is leading the Bundesliga table?"

BUNDESLIGA_DATA = "Tabelle: 1. Bayer Leverkusen - 25 Punkte, 2. Bayern München - 23 Punkte"

SYSTEM_PROMPT = "Du bist ein deutscher Sportjournalist. Antworte kurz und präzise auf Deutsch."

print(f"Testing bilingual demo...")
print(f"Question (EN): {TEST_QUERY_EN}")
print(f"Question (DE): {TEST_QUERY_DE}\n")

print("Step 1: Getting German response...")
try:
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{BUNDESLIGA_DATA}"},
            {"role": "user", "content": TEST_QUERY_DE}
        ],
        max_tokens=500
    )

    german_answer = response.choices[0].message.content
    print(f"✅ German Response:\n{german_answer}\n")

except Exception as e:
    print(f"❌ Error getting German response: {str(e)}\n")
    exit(1)

print("Step 2: Translating to English...")
try:
    translation = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translator. Translate the following German sports text to English. Maintain the tone."
            },
            {"role": "user", "content": german_answer}
        ],
        max_tokens=500,
        temperature=0.3
    )

    english_answer = translation.choices[0].message.content
    print(f"✅ English Translation:\n{english_answer}\n")

    print("✅ Bilingual demo test successful!\n")

except Exception as e:
    print(f"❌ Error translating: {str(e)}\n")
    exit(1)
