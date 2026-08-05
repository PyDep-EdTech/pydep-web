#!/usr/bin/env bash
# Mac: весь DNS через Technitium. Зоны — только в http://127.0.0.1:5380
# Без /etc/resolver на каждую зону (если VPN не перехватывает DNS).
set -euo pipefail

TS_IP="$(tailscale ip -4 2>/dev/null || true)"

echo "==> Проверка: не перехватывает ли VPN DNS..."
if scutil --dns 2>/dev/null | rg -q "nameserver\[0\] : 10\.0\.0\.20"; then
  echo ""
  echo "ОШИБКА: VPN (utun4, xeovo/v2Ray) подставляет DNS 10.0.0.20."
  echo "Пока это не исправлено, macOS не будет ходить только в Technitium."
  echo ""
  echo "Исправление (один раз в VPN-клиенте):"
  echo "  xeovo / WireGuard → профиль → DNS = 127.0.0.1  (вместо 10.0.0.20)"
  echo "  или отключите «DNS через VPN» / «Use VPN DNS»"
  echo ""
  echo "После смены DNS в VPN переподключитесь и запустите этот скрипт снова."
  exit 1
fi

echo "==> Tailscale IP: ${TS_IP:-не найден}"

echo "==> Отключаем DNS от Tailscale на этом Mac"
tailscale set --accept-dns=false

echo "==> Системный DNS → 127.0.0.1 на всех интерфейсах"
while IFS= read -r svc; do
  [[ "$svc" == *"*"* ]] && continue
  if networksetup -setdnsservers "$svc" 127.0.0.1 2>/dev/null; then
    echo "    $svc"
  fi
done < <(networksetup -listallnetworkservices)

echo "==> Удаляем /etc/resolver для отдельных зон (не нужны)"
sudo mkdir -p /etc/resolver/backup
for f in /etc/resolver/home.server /etc/resolver/domain.test.zone; do
  if [[ -f "$f" ]]; then
    sudo mv "$f" "/etc/resolver/backup/$(basename "$f").$(date +%Y%m%d)"
    echo "    backup: $f"
  fi
done

echo "==> Сброс DNS-кэша"
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true

echo ""
echo "Готово. Новые зоны — только в Technitium, без правок на Mac."
echo ""
echo "Проверка:"
echo "  ping domain.test.zone"
echo "  ping macbook.home.server"
echo "  dig @127.0.0.1 google.com +short"
echo ""
echo "Tailscale Admin (один раз): Nameserver ${TS_IP:-100.x.x.x} + Override local DNS"
