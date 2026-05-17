#!/usr/bin/env bash
# Запуск всех 3 проектов одновременно (каждый на своём порту)
# Логи: /tmp/<имя_проекта>.log

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

start_one() {
  local name="$1" port="$2"
  cd "$ROOT/$name"
  nohup ./venv/bin/python manage.py runserver "0.0.0.0:$port" \
    > "/tmp/${name}.log" 2>&1 &
  disown
  echo "  ✓ $name → http://127.0.0.1:$port  (PID $!)"
}

echo "Останавливаем старые runserver'ы..."
pkill -f "manage.py runserver" 2>/dev/null || true
sleep 1

echo "Запускаем 3 сервера..."
start_one barber_crm    8765
start_one auto_service  8766
start_one laundry_pos   8767

sleep 2
echo
echo "Проверка:"
for p in 8765 8766 8767; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$p/" || echo "FAIL")
  printf "  port %s → %s\n" "$p" "$code"
done
echo
echo "Логи в реальном времени:"
echo "  tail -f /tmp/barber_crm.log /tmp/auto_service.log /tmp/laundry_pos.log"
echo "Остановить всё: $ROOT/stop_all.sh"
