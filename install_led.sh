#!/bin/bash
# Instalator modułu LED Display
# YO&GO Events - 2025

echo "=========================================="
echo "LED Display Module - Instalator"
echo "YO&GO Events - 2025"
echo "=========================================="
echo ""

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo "   Zainstaluj Python 3.7 lub nowszy z python.org"
    exit 1
fi

echo "✅ Python wykryty: $(python3 --version)"
echo ""

# Sprawdź czy pip jest zainstalowany
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip nie jest zainstalowany!"
    echo "   Zainstaluj pip: sudo apt-get install python3-pip"
    exit 1
fi

echo "✅ pip wykryty"
echo ""

# Instaluj zależności
echo "📦 Instaluję zależności..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Zależności zainstalowane!"
else
    echo "❌ Błąd instalacji zależności"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Instalacja zakończona!"
echo "=========================================="
echo ""
echo "Następne kroki:"
echo "1. Podłącz tablicę LED do portu COM"
echo "2. Uruchom: python3 led_autotest.py"
echo "3. Zanotuj który baudrate działa"
echo "4. Uruchom: python3 led_demo.py"
echo "5. Przeczytaj: LED_INTEGRATION.md"
echo ""
echo "Powodzenia! 🎉"
