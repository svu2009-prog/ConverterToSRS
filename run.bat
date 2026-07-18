@echo off
chcp 65001 >nul
title List Processor for sing-box

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Установите Python 3.12+ и повторите запуск.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo requirements.txt не найден.
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt -q

echo Запуск приложения...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Произошла ошибка. Нажмите любую клавишу для выхода.
    pause
)
