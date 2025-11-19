@echo off
REM Instalator modułu LED Display
REM YO&GO Events - 2025

echo ==========================================
echo LED Display Module - Instalator
echo YO^&GO Events - 2025
echo ==========================================
echo.

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nie jest zainstalowany!
    echo    Zainstaluj Python 3.7 lub nowszy z python.org
    pause
    exit /b 1
)

echo ✅ Python wykryty
python --version
echo.

REM Instaluj zależności
echo 📦 Instaluję zależności...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Błąd instalacji zależności
    pause
    exit /b 1
)

echo ✅ Zależności zainstalowane!
echo.

echo ==========================================
echo ✅ Instalacja zakończona!
echo ==========================================
echo.
echo Następne kroki:
echo 1. Podłącz tablicę LED do portu COM
echo 2. Uruchom: python led_autotest.py
echo 3. Zanotuj który baudrate działa
echo 4. Uruchom: python led_demo.py
echo 5. Przeczytaj: LED_INTEGRATION.md
echo.
echo Powodzenia! 🎉
echo.
pause
