@echo off
chcp 65001 >nul
title Chronometr LED - YO&GO Events
color 0A

echo ============================================
echo    CHRONOMETR LED - YO&GO Events
echo ============================================
echo.

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo [BŁĄD] Python nie jest zainstalowany!
    echo.
    echo Pobierz Python z: https://www.python.org/downloads/
    echo WAŻNE: Podczas instalacji zaznacz "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python znaleziony
echo.

REM Sprawdź czy pyserial jest zainstalowany
python -c "import serial" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instaluję wymagane biblioteki...
    python -m pip install --quiet pyserial
    if errorlevel 1 (
        echo [BŁĄD] Nie udało się zainstalować bibliotek!
        pause
        exit /b 1
    )
    echo [OK] Biblioteki zainstalowane
    echo.
)

echo [START] Uruchamiam chronometr...
echo.
echo ============================================
echo.

REM Uruchom aplikację
python chronometr_v5_LED.py

REM Jeśli program się zamknął z błędem, zatrzymaj okno
if errorlevel 1 (
    echo.
    echo ============================================
    echo [BŁĄD] Program zakończył się z błędem!
    echo ============================================
    pause
)
