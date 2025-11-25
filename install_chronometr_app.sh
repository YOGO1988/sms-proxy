#!/bin/bash
# Skrypt instalacyjny dla aplikacji Chronometr Manager v5 LED

echo "================================================"
echo "INSTALACJA: Chronometr Manager v5 LED"
echo "================================================"

# Katalog dla aplikacji użytkownika
APPS_DIR="$HOME/.local/share/applications"

# Upewnij się, że katalog istnieje
mkdir -p "$APPS_DIR"

# Skopiuj plik .desktop
echo "Kopiowanie pliku .desktop do $APPS_DIR..."
cp /home/user/sms-proxy/Chronometr.desktop "$APPS_DIR/"

# Nadaj uprawnienia
chmod +x "$APPS_DIR/Chronometr.desktop"

# Odśwież bazę danych aplikacji
if command -v update-desktop-database &> /dev/null; then
    echo "Odświeżanie bazy danych aplikacji..."
    update-desktop-database "$APPS_DIR"
fi

echo ""
echo "✅ INSTALACJA ZAKOŃCZONA!"
echo ""
echo "Aplikacja 'Chronometr Manager v5 LED' jest teraz dostępna:"
echo "  • W menu aplikacji (szukaj: Chronometr)"
echo "  • Możesz też kliknąć podwójnie plik: Chronometr.desktop"
echo ""
echo "Aby odinstalować, usuń plik:"
echo "  rm $APPS_DIR/Chronometr.desktop"
echo ""
