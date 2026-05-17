# BMI Deploy notes (server: srvr1.sammu.uz)

## Persistent stack (active)

3 ta Django loyiha (Barber/Auto/Laundry) supervisord orqali boshqariladi va PHP-FPM watchdog tufayli jailbash sessiyalardan mustaqil ishlaydi.

### Supervisord servislari

```
bmi-barber-web      gunicorn  127.0.0.1:8765
bmi-barber-tunnel   cloudflared → :8765
bmi-auto-web        gunicorn  127.0.0.1:8766
bmi-auto-tunnel     cloudflared → :8766
bmi-laundry-web     gunicorn  127.0.0.1:8767
bmi-laundry-tunnel  cloudflared → :8767
```

Confs: `~/.config/supervisor/conf.d/bmi-*.conf`
Logs:  `~/logs/bmi/`

### Boshqaruv

```bash
SUP=/home/hsm/.local/bin/supervisorctl
CONF=/home/hsm/.config/supervisor/supervisord.conf

$SUP -c $CONF status                          # holatni ko'rish
$SUP -c $CONF restart bmi-barber-web          # bitta restart
$SUP -c $CONF restart 'bmi-*'                 # hammasi
$SUP -c $CONF tail -f bmi-barber-web stderr   # log oqimi

# Conf o'zgartirilgan bo'lsa:
$SUP -c $CONF reread && $SUP -c $CONF update
```

### Public URL'larni topish

```bash
for n in barber auto laundry; do
  url=$(grep -hoE 'https://[a-z0-9-]+\.trycloudflare\.com' \
        ~/logs/bmi/$n-tunnel.err.log ~/logs/bmi/$n-tunnel.log 2>/dev/null | head -1)
  printf "%-8s → %s\n" "$n" "$url"
done
```

URL faqat tunnel **restart bo'lganda** o'zgaradi.

## Fallback: runserver

`gunicorn` muammo chiqarsa (masalan WhiteNoise CSS conflict, async view kerak bo'lsa), web qatlamini `manage.py runserver` ga qaytarish mumkin. Buning uchun har conf'da `command=` qatorini quyidagicha o'zgartiring:

```
command=/home/hsm/apps/bmi/<project>/venv/bin/python manage.py runserver 127.0.0.1:<port>
```

Va `directory=` o'zgarmaydi. Keyin `supervisorctl reread && update`.

Eslatma: runserver static fayllarni avtomatik beradi — WhiteNoise middleware'ni `MIDDLEWARE` ro'yxatidan olib tashlash shart emas, lekin foydasiz bo'ladi.

## Manual demo skriptlari (eski variant, supervisorсиз)

`run_all.sh`, `stop_all.sh`, `tunnel_all.sh` — repoda mavjud, lekin **jailbash session tugaganda barcha jarayonlar o'ladi** (`--die-with-parent`). Faqat lokal mashinada yoki uzoq SSH session uchun mos.
