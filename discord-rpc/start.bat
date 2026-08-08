@echo off
echo ========================================
echo   Discord RPC Manager
echo ========================================
echo.

cd /d "%~dp0"

if not exist node_modules (
    echo Установка зависимостей...
    npm install
    echo.
)

echo Запуск сервера...
echo Откройте http://localhost:3000 в браузере
echo.
node server.js
pause
