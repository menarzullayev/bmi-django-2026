#!/usr/bin/env bash
# Запускает 3 туннеля Cloudflare (trycloudflare.com) — по одному на каждый проект.
# Требует установленный cloudflared. Сначала запустите ./run_all.sh
#
# Установка cloudflared (Ubuntu/Debian):
#   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cf.deb
#   sudo dpkg -i /tmp/cf.deb

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/.tunnels"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "❌ cloudflared не установлен."
  echo "   Установите: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/install-and-setup/installation/"
  exit 1
fi

start_tunnel() {
  local name="$1" port="$2"
  local log="$ROOT/.tunnels/${name}.log"
  : > "$log"
  nohup cloudflared tunnel --no-autoupdate --url "http://localhost:$port" > "$log" 2>&1 &
  disown
  echo "  $name (порт $port) → лог: $log"
}

echo "Останавливаем старые туннели..."
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 1

echo "Запускаем туннели..."
start_tunnel barber   8765
start_tunnel auto     8766
start_tunnel laundry  8767

echo
echo "Ждём ~8 секунд, чтобы Cloudflare выдал URL..."
sleep 8

echo
echo "════════════════════════════════════════════════════════"
echo "  Публичные URL"
echo "════════════════════════════════════════════════════════"
for name in barber auto laundry; do
  url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$ROOT/.tunnels/${name}.log" | head -1)
  if [ -n "$url" ]; then
    printf "  %-10s → %s\n" "$name" "$url"
  else
    printf "  %-10s → (ещё не готов, см. %s)\n" "$name" "$ROOT/.tunnels/${name}.log"
  fi
done
echo "════════════════════════════════════════════════════════"
echo
echo "Остановить туннели: pkill -f 'cloudflared tunnel'"
