@echo off
chcp 65001 >nul
title Chronometr LED - YO&GO Events
color 0A

REM Przejdź do katalogu gdzie znajduje się ten skrypt
cd /d "%~dp0"

echo ============================================
echo    CHRONOMETR LED - YO&GO Events
echo ============================================
echo.
echo Katalog roboczy: %CD%
echo.

REM Sprawdź czy plik chronometr_v5_LED.py istnieje
if not exist "chronometr_v5_LED.py" (
    echo [BŁĄD] Nie znaleziono pliku chronometr_v5_LED.py!
    echo.
    echo Upewnij się, że plik uruchom_chronometr.bat znajduje się
    echo w tym samym folderze co chronometr_v5_LED.py
    echo.
    pause
    exit /b 1
)

REM Sprawdź czy Python jest zainstalowany
echo [INFO] Sprawdzam instalację Python...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo [BŁĄD] Python nie jest zainstalowany lub nie jest w PATH!
    echo.
    echo Pobierz Python z: https://www.python.org/downloads/
    echo WAŻNE: Podczas instalacji zaznacz "Add Python to PATH"
    echo.
    echo Alternatywnie spróbuj użyć komendy: py --version
    echo.
    pause
    exit /b 1
)

echo [OK] Python znaleziony
echo.

REM Sprawdź czy pyserial jest zainstalowany
echo [INFO] Sprawdzam bibliotekę pyserial...
python -c "import serial" 2>nul
if errorlevel 1 (
    echo [INFO] Instaluję wymagane biblioteki (pyserial)...
    echo.
    python -m pip install pyserial
    if errorlevel 1 (
        echo.
        echo [BŁĄD] Nie udało się zainstalować bibliotek!
        echo Spróbuj ręcznie: python -m pip install pyserial
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Biblioteki zainstalowane
    echo.
)

echo [OK] Wszystkie wymagania spełnione
echo.
echo ============================================
echo [START] Uruchamiam chronometr...
echo ============================================
echo.

REM Uruchom aplikację
python chronometr_v5_LED.py

REM Zawsze zatrzymaj okno po zamknięciu programu
echo.
echo ============================================
echo Program został zamknięty
echo ============================================
pause
