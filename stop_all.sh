#!/usr/bin/env bash
# Останавливает все 3 runserver
pkill -f "manage.py runserver" 2>/dev/null && echo "✓ Все серверы остановлены" || echo "Нет работающих runserver'ов"
