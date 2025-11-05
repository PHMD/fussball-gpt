#!/bin/bash
# KSI Demo - Easy Launch Script

echo ""
echo "🎯 KSI Demo - Kicker Sports Intelligence"
echo "========================================"
echo ""
echo "Powered by Mistral Large"
echo "Quality: 7.33/10 | Speed: ~3.6s avg"
echo ""
echo "Choose demo mode:"
echo ""
echo "  [1] English Testing (with translations) 🌍"
echo "  [2] German Only (for Kicker team) 🇩🇪"
echo "  [3] Quick Test (verify it works) ⚡"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting BILINGUAL demo (German + English translations)..."
        echo "📖 See TESTING_GUIDE_ENGLISH.md for testing instructions"
        echo ""
        sleep 1
        source venv/bin/activate && python ksi_demo_bilingual.py --bilingual
        ;;
    2)
        echo ""
        echo "Starting GERMAN-ONLY demo..."
        echo "📖 See README_DEMO.md for instructions"
        echo ""
        sleep 1
        source venv/bin/activate && python ksi_demo.py
        ;;
    3)
        echo ""
        echo "Running quick verification test..."
        echo ""
        source venv/bin/activate && python test_bilingual_demo.py
        ;;
    *)
        echo ""
        echo "Invalid choice. Please run again and choose 1, 2, or 3."
        exit 1
        ;;
esac
