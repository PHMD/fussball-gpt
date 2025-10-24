"""Interactive user onboarding."""
from user_config import UserConfigManager, DetailLevel, Language


def run_onboarding():
    """Interactive onboarding to set up user preferences."""

    print("\n" + "="*70)
    print("  ⚽ Willkommen bei Fußball GPT / Welcome to Fußball GPT")
    print("="*70)
    print("\nLet's set up your preferences / Lass uns deine Einstellungen konfigurieren.\n")

    config = UserConfigManager()

    # Question 1: Language (FIRST - determines rest of flow)
    print("Preferred language / Bevorzugte Sprache?")
    print("1. 🇩🇪 Deutsch")
    print("2. 🇬🇧 English")
    print()

    while True:
        choice = input("Your choice / Deine Wahl (1-2): ").strip()
        if choice == "1":
            config.profile.language = Language.GERMAN
            lang = "de"
            break
        elif choice == "2":
            config.profile.language = Language.ENGLISH
            lang = "en"
            break
        else:
            print("Please choose 1 or 2 / Bitte 1 oder 2 wählen.")

    # Save language choice before continuing
    config.save_profile()

    # Question 2: Name (optional)
    if lang == "de":
        name = input("\nWie sollen wir dich nennen? (Enter für 'User'): ").strip()
        if name:
            config.profile.name = name

        # Question 3: Detail Level (CRITICAL)
        print(f"\n{config.profile.name}, wie detailliert sollen meine Antworten sein?\n")
        print("1. 🚀 SCHNELL - Kurze Highlights (1-2 Sätze)")
        print("   Beispiel: 'Bayern führt mit 82 Punkten, 13 vor Leverkusen.'")
        print()
        print("2. ⚖️  AUSGEWOGEN - Standard-Journalismus (2-3 Absätze) [EMPFOHLEN]")
        print("   Beispiel: Bayern-Analyse + Kontext + ein bisschen Taktik")
        print()
        print("3. 📊 DETAILLIERT - Tiefe Analysen (3-5+ Absätze)")
        print("   Beispiel: Formationen, Systeme, Statistiken, Vergleiche")
        print()

        while True:
            choice = input("Deine Wahl (1-3): ").strip()
            if choice == "1":
                config.profile.detail_level = DetailLevel.QUICK
                print("✅ Eingestellt: Schnelle, prägnante Antworten")
                break
            elif choice == "2":
                config.profile.detail_level = DetailLevel.BALANCED
                print("✅ Eingestellt: Ausgewogene Antworten (Standard)")
                break
            elif choice == "3":
                config.profile.detail_level = DetailLevel.DETAILED
                print("✅ Eingestellt: Detaillierte, analytische Antworten")
                break
            else:
                print("Bitte 1, 2 oder 3 wählen.")

        # Question 4: Favorite Team (optional)
        print("\nHast du ein Lieblingsteam? (Enter zum Überspringen)")
        team = input("Team: ").strip()
        if team:
            config.profile.favorite_team = team
            print(f"✅ Lieblingsteam: {team}")

    else:  # English
        name = input("\nWhat should we call you? (Enter for 'User'): ").strip()
        if name:
            config.profile.name = name

        # Question 3: Detail Level (CRITICAL)
        print(f"\n{config.profile.name}, how detailed should my answers be?\n")
        print("1. 🚀 QUICK - Short highlights (1-2 sentences)")
        print("   Example: 'Bayern leads with 82 points, 13 ahead of Leverkusen.'")
        print()
        print("2. ⚖️  BALANCED - Standard journalism (2-3 paragraphs) [RECOMMENDED]")
        print("   Example: Bayern analysis + context + some tactics")
        print()
        print("3. 📊 DETAILED - In-depth analysis (3-5+ paragraphs)")
        print("   Example: Formations, systems, statistics, comparisons")
        print()

        while True:
            choice = input("Your choice (1-3): ").strip()
            if choice == "1":
                config.profile.detail_level = DetailLevel.QUICK
                print("✅ Set to: Quick, concise answers")
                break
            elif choice == "2":
                config.profile.detail_level = DetailLevel.BALANCED
                print("✅ Set to: Balanced answers (default)")
                break
            elif choice == "3":
                config.profile.detail_level = DetailLevel.DETAILED
                print("✅ Set to: Detailed, analytical answers")
                break
            else:
                print("Please choose 1, 2, or 3.")

        # Question 4: Favorite Team (optional)
        print("\nDo you have a favorite team? (Enter to skip)")
        team = input("Team: ").strip()
        if team:
            config.profile.favorite_team = team
            print(f"✅ Favorite team: {team}")

    # Save profile
    config.save_profile()

    if lang == "de":
        print("\n" + "="*70)
        print("✅ Einrichtung abgeschlossen!")
        print(f"Deine Einstellungen wurden in '.fussballgpt_config.json' gespeichert.")
        print()
        print("Du kannst diese jederzeit ändern mit: python onboarding.py")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("✅ Setup complete!")
        print(f"Your settings have been saved to '.fussballgpt_config.json'.")
        print()
        print("You can change these anytime with: python onboarding.py")
        print("="*70 + "\n")

    return config.profile


if __name__ == "__main__":
    run_onboarding()
