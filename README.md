# 3 BMI loyihalari — Django bundle

Uchta diplom (BMI) loyihasi bitta papkada. Bir xil stack (Django 5 + HTMX + Tailwind CSS + SQLite), lekin har biri o'ziga xos arxitektura, UI/UX va workflow ga ega. Frontend butunlay **rus tilida**.

Rahbar: **Убайдуллаев М.** · Guruh: **DI-O22-04** · Tayyorlangan: **2026-05-17**

| # | Mavzu (asl matn) | Talaba | Papka | Port |
|---|------------------|--------|-------|------|
| 35 | Создание программного обеспечения для управления записями и клиентской базой парикмахерской | Журакулова Дилнавоз Мехриддин қизи | [`barber_crm/`](barber_crm/) | **8765** |
| 36 | Создание системы управления заказами и клиентской базой в автосервисе | Бахронкулов Шодиёр Ирисбой ўғли | [`auto_service/`](auto_service/) | **8766** |
| 37 | Разработка программного обеспечения для учёта заказов и клиентов в химчистке | Примова Дилноза Хужамшукуровна | [`laundry_pos/`](laundry_pos/) | **8767** |

---

## Tarkib

```
Django_projects/
├── README.md            ← Bu fayl
├── ROADMAP.md           ← Loyihalar rejasi (BMI metadata bilan)
├── run_all.sh           ← 3 ta serverni parallel ishga tushiradi
├── stop_all.sh          ← 3 ta serverni to'xtatadi
├── tunnel_all.sh        ← Cloudflare tunnellarni ochadi (public URL)
├── barber_crm/          ← #35 Sartaroshxona (Журакулова)
│   ├── config/ accounts/ clients/ staff/ services/ bookings/ loyalty/ liveline/ core/
│   ├── templates/       ← 20 ta HTML (rus tilida)
│   ├── manage.py, db.sqlite3, requirements.txt, README.md, STATUS.md
│   └── venv/            ← ⚠️ KO'CHIRMANG, serverda qaytadan yarating
├── auto_service/        ← #36 Avtoservis (Бахронкулов)
│   ├── config/ accounts/ customers/ vehicles/ workorders/ parts/ workflow/ billing/ mechanics/ core/
│   ├── templates/       ← 30 ta HTML
│   └── ... (manage.py, db.sqlite3, requirements.txt, README.md, STATUS.md, venv/)
└── laundry_pos/         ← #37 Химчистка (Примова)
    ├── config/ accounts/ customers/ catalog/ intake/ payments/ delivery/ reports/ core/
    ├── templates/       ← 26 ta HTML
    └── ... (manage.py, db.sqlite3, requirements.txt, README.md, STATUS.md, venv/)
```

---

## Tezkor ishga tushirish (loyihalar allaqachon o'rnatilgan bo'lsa)

```bash
cd ~/Django_projects
./run_all.sh        # 3 ta server parallel
# brauzerda: http://127.0.0.1:8765 / :8766 / :8767
./stop_all.sh       # tugatish
```

Login (uchchalasi uchun ham): `admin` / `admin123`

---

## 1. Serverga ko'chirish

### 1.1. Faqat kerakli narsalar (engil — venv siz)

`venv/` ni ko'chirmang — uning ichida absolute pathlar bor, boshqa joyda buzilib qoladi. `db.sqlite3` ham ixtiyoriy — yangi serverda seed orqali tiklash mumkin.

`rsync` bilan:

```bash
# lokal kompyuterda (manba)
rsync -avh --exclude='venv/' --exclude='__pycache__/' --exclude='.tunnels/' \
  ~/Django_projects/ user@your-server:/home/user/Django_projects/
```

Yoki `tar` bilan:

```bash
# manbada
cd ~
tar --exclude='Django_projects/*/venv' \
    --exclude='Django_projects/*/__pycache__' \
    --exclude='Django_projects/*/*/__pycache__' \
    --exclude='Django_projects/.tunnels' \
    -czvf bmi.tar.gz Django_projects/

# serverga ko'chirish
scp bmi.tar.gz user@your-server:/home/user/

# serverda
cd ~ && tar -xzvf bmi.tar.gz
```

### 1.2. Hammasini ko'chirish (venv bilan birga — tavsiya etilmaydi)

Faqat **bir xil arxitektura va OS** (Linux x86_64, Python 3.12) bo'lsa ishlaydi:

```bash
rsync -avh ~/Django_projects/ user@your-server:/home/user/Django_projects/
```

Lekin baribir serverda `venv/bin/activate` ichidagi pathlar buzilgan bo'ladi — to'liq qayta yaratish yaxshiroq.

---

## 2. Serverda o'rnatish

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-venv python3-pip fonts-dejavu-core curl
# fonts-dejavu-core — PDF da kirillchada matn chiqishi uchun
```

`python3 --version` → 3.10+ bo'lishi kerak (3.12 da test qilingan).

### Har loyiha uchun bir martalik setup

```bash
cd ~/Django_projects/barber_crm        # yoki auto_service / laundry_pos
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data             # demo ma'lumotlar
deactivate
```

Uchchalasi uchun ham takrorlang. Yoki bir buyruqda:

```bash
cd ~/Django_projects
for p in barber_crm auto_service laundry_pos; do
  ( cd "$p" && python3 -m venv venv && \
    ./venv/bin/pip install -r requirements.txt && \
    ./venv/bin/python manage.py migrate && \
    ./venv/bin/python manage.py seed_data )
done
```

---

## 3. Ishga tushirish

### Hammasini bir vaqtda

```bash
cd ~/Django_projects
./run_all.sh
```

Natija:
```
✓ barber_crm → http://127.0.0.1:8765
✓ auto_service → http://127.0.0.1:8766
✓ laundry_pos → http://127.0.0.1:8767
port 8765 → 200
port 8766 → 302
port 8767 → 302
```

302 — auth-protected sahifa login ga redirect qilmoqda (to'g'ri).

### Faqat birini

```bash
cd ~/Django_projects/barber_crm
source venv/bin/activate
python manage.py runserver 0.0.0.0:8765
```

### Loglarni kuzatish

```bash
tail -f /tmp/barber_crm.log /tmp/auto_service.log /tmp/laundry_pos.log
```

### To'xtatish

```bash
./stop_all.sh
```

---

## 4. Cloudflare Tunnel (`trycloudflare.com`) bilan public URL

### Cloudflared o'rnatish

```bash
# Ubuntu/Debian
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cf.deb
sudo dpkg -i /tmp/cf.deb
cloudflared --version
```

### Bir loyihaga URL olish

```bash
cloudflared tunnel --url http://localhost:8765
```

Output:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://random-words-here.trycloudflare.com                                               |
+--------------------------------------------------------------------------------------------+
```

### 3 ta URL ni bir vaqtda olish

```bash
./run_all.sh        # avval Django serverlari ishga tushsin
./tunnel_all.sh     # so'ng 3 tunnel
```

Output:
```
════════════════════════════════════════════════════════
  Публичные URL
════════════════════════════════════════════════════════
  barber     → https://aaaa-bbbb-cccc.trycloudflare.com
  auto       → https://dddd-eeee-ffff.trycloudflare.com
  laundry    → https://gggg-hhhh-iiii.trycloudflare.com
════════════════════════════════════════════════════════
```

URL'lar `cloudflared` to'xtatilganda yo'qoladi (har safar yangisi beriladi).

### To'xtatish

```bash
pkill -f "cloudflared tunnel"
```

---

## 5. Trycloudflare uchun sozlamalar (allaqachon qilingan)

Har 3 `config/settings.py` ga qo'shildi:

```python
ALLOWED_HOSTS = ['*']                          # barcha hostlar (DEBUG=True uchun OK)

CSRF_TRUSTED_ORIGINS = [
    'https://*.trycloudflare.com',             # POST formlar HTTPS public URL orqali ishlashi uchun
    'https://*.cfargotunnel.com',
]

SESSION_COOKIE_NAME = '<prefix>_sessionid'     # 3 loyiha cookie collision oldini olish uchun
CSRF_COOKIE_NAME = '<prefix>_csrftoken'        # (prefix: barber / auto / laundry)
```

Shu sabab uchchalasi bir vaqtda bir domenda (yoki localhost da 3 portda) muammosiz ishlaydi.

---

## 6. Login va demo ma'lumotlar

### Hammasi uchun
- **Admin (superuser):** `admin` / `admin123`
- **Django admin paneli:** `/admin/`

### Barber CRM (port 8765, prefix `barber`)
| Login | Parol | Rol |
|-------|-------|-----|
| `admin` | `admin123` | Администратор |
| `master1`–`master4` | `master123` | Мастер |
| `client1`–`client15` | `client123` | Клиент |
| (har qanday telefon) | OTP: `123456` | mock kirish |

Seed: 15 mijoz, 4 usta, 6 kategoriya, 20 xizmat, 33 zapis, 50 loyalty tranzaksiyasi.

### Auto Service (port 8766, prefix `auto`)
| Login | Parol | Rol |
|-------|-------|-----|
| `admin` | `admin123` | Администратор |
| `reception` | `admin123` | Приёмщик |
| `mechanic1`–`mechanic4` | `admin123` | Механик |

Seed: 25 mijoz, 35 avto, 162 zapchast, 40 zakaz-naryad, 6 schyot. PDF schyot mavjud.

### Laundry POS (port 8767, prefix `laundry`)
| Login | Parol | Rol |
|-------|-------|-----|
| `admin` | `admin123` | Администратор |
| `cashier1`–`cashier2` | `admin123` | Кассир |
| `operator` | `admin123` | Оператор |
| `driver1`–`driver2` | `admin123` | Водитель |

Seed: 30 mijoz, 12 cloth type, 6 service type, 72 narx, 50 квитанция, 208 garment, 27 to'lov, 5 yetkazib berish marshruti.

Public QR URL (loginsiz): `/qr/T-20260517-0001/` — mijoz tomon status tekshiruvi.

---

## 7. Maxsus demo URL'lar (taqdimot uchun foydali)

| Loyiha | URL | Tavsif |
|--------|-----|--------|
| Barber | `/` | Lendinp с gradient hero |
| Barber | `/booking/` | HTMX booking calendar |
| Barber | `/me/loyalty/` | Loyalty programmasi (login) |
| Auto | `/dashboard/` | KPI dashboard + Chart.js |
| Auto | `/kanban/` | Kanban board |
| Auto | `/invoices/1/pdf/` | **PDF schyot** (DejaVuSans Cyrillic) |
| Laundry | `/pos/` | POS dashboard |
| Laundry | `/intake/new/` | POS-style intake form (HTMX) |
| Laundry | `/pricing/` | Inline edit narx matrisi (HTMX) |
| Laundry | `/qr/T-20260517-0001/` | **Public QR status (no login)** |
| Laundry | `/tickets/1/receipt/pdf/` | PDF kvitansiya |

---

## 8. Xatolar yoki muammolar

### `CSRF verification failed` (403)
- Brauzerda eski cookie'larni tozalang (DevTools → Application → Cookies)
- Yoki har loyihani **Incognito** oynada oching
- Yoki `Ctrl+Shift+R` bilan qattiq yangilang
- Cloudflare URL orqali bo'lsa — settings.py'da `CSRF_TRUSTED_ORIGINS` `https://*.trycloudflare.com` borligini tekshiring (allaqachon qo'shilgan)

### `ModuleNotFoundError: No module named 'django'`
- venv aktivlashtirilmagan: `source venv/bin/activate`
- yoki venv yaratilmagan: `python3 -m venv venv && pip install -r requirements.txt`

### `port already in use`
- `./stop_all.sh` bilan oldingilarni to'xtating
- yoki `lsof -i :8765` orqali tekshiring

### PDF da kirillcha matn quti (□□□) bo'lib chiqsa
- `fonts-dejavu-core` o'rnatilmagan: `sudo apt install fonts-dejavu-core`
- Yoki `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` mavjudligini tekshiring

### Cloudflare URL "522" qaytaradi
- Django server ishlamayapti — `./run_all.sh` qiling
- Yoki Django boshqa portda — `tunnel_all.sh` ichidagi portni tekshiring

---

## 9. Production uchun (kelajakda)

Hozir `DEBUG = True`, `ALLOWED_HOSTS = ['*']`. Bu **faqat dev** uchun. Real production uchun:

```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', '*.your-domain.com']
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']    # env'dan o'qing
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

`runserver` o'rniga `gunicorn` ishlatish:

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8765
```

Static fayllar uchun:

```bash
python manage.py collectstatic --noinput
# va nginx orqali servings
```

---

## 10. Texnik xulosa

| Element | Barber | Auto | Laundry |
|---------|--------|------|---------|
| **Stack** | Django 5.1 + HTMX 2 + Tailwind CDN + SQLite | (same) | (same) |
| **Layout** | Top nav + mobile bottom tab | Fixed dark sidebar | Top horizontal bar |
| **Rang** | Indigo→Purple→Pink gradient | Dark gray + orange-500 | Cyan + blue |
| **Font** | Poppins | Inter | Nunito |
| **Radius** | `rounded-2xl` | `rounded-md` | `rounded-md` (sharp) |
| **Auth** | Phone OTP mock | Role-based classic | Cashier role |
| **Asosiy feature** | Booking calendar + loyalty | Kanban workflow + parts | POS intake + receipt PDF + QR |
| **Apps soni** | 8 | 9 | 8 |
| **Models** | ~248 lines | ~449 lines | ~308 lines |
| **Views** | ~422 lines | ~878 lines | ~720 lines |
| **Templates** | 20 ta | 30 ta | 26 ta |
| **DB hajmi** | 228 KB | 292 KB | 280 KB |

Uchchalasi ham bir xil stack ustida, lekin **arxitektura, URL terminologiyasi, model nomlari, UI komponentlari, ranglar, fontlar va biznes mantiqi butunlay boshqa**.

---

## License

Faqat ta'lim maqsadlarida (BMI/diplom ishi). Ishlab chiqaruvchi: Claude Opus 4.7 + Claude Code agent harness.
