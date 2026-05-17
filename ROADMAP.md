# BMI Loyihalari — Roadmap

**Sana:** 2026-05-17
**Stack:** Django 5.x + HTMX + Tailwind CSS + SQLite
**Strategiya:** Bir xil stack, har xil arxitektura/UI/UX/workflow
**Frontend tili:** 🇷🇺 РУССКИЙ (barcha UI matnlari rus tilida)
**Rahbar:** Ubaydullayev M.
**Guruh:** DI-O22-04

## Rasmiy BMI ro'yxatidagi mavzular

| № | Mavzu (asl matn) | Talaba | Ball | Papka |
|---|-----------------|--------|------|-------|
| 35 | Создание программного обеспечения для управления записями и клиентской базой парикмахерской | Juraqulova Dilnavoz Mexriddin qizi | 80 | `barber_crm/` |
| 36 | Создание системы управления заказами и клиентской базой в автосервисе | Baxronkulov Shodiyor Irisboy o'g'li | 75 | `auto_service/` |
| 37 | Разработка программного обеспечения для учёта заказов и клиентов в химчистке | Primova Dilnoza Xujamshukurovna | 80 | `laundry_pos/` |

---

## Loyihalar

### 1. Barber CRM (`barber_crm/`)
- **Fokus:** Booking-centric (mijoz buyurtma berishga qaratilgan)
- **Style:** Modern mobile-first SaaS
- **Rang:** Purple/Indigo gradient
- **Font:** Poppins
- **Layout:** Top tabs + card-heavy, mobile feeling
- **Auth:** Phone OTP (mock — kodni terminalga chiqarish)
- **Key features:**
  - Online booking with calendar
  - Barber schedule
  - Real-time queue management
  - Loyalty points system
  - Customer avatars
  - Service catalog
  - SMS/Telegram reminder (mock)

### 2. Auto Service (`auto_service/`)
- **Fokus:** Workflow-centric (ish jarayonini boshqarish)
- **Style:** Industrial/ERP admin dashboard
- **Rang:** Orange + Dark Gray
- **Font:** Inter
- **Layout:** Dark sidebar + tables + Kanban-heavy
- **Auth:** Classic admin login (role-based: admin / receptionist / mechanic)
- **Key features:**
  - Work order lifecycle (FSM)
  - Kanban workflow board (received → diagnosed → in_repair → quality_check → completed)
  - Spare parts inventory
  - Mechanic assignment & workload
  - Vehicle history
  - Repair cost calculation
  - Invoice generation

### 3. Laundry POS (`laundry_pos/`)
- **Fokus:** Accounting + logistics-centric (kassa va yetkazib berish)
- **Style:** Clean/lightweight POS system
- **Rang:** Cyan/Blue
- **Font:** Nunito
- **Layout:** Compact POS navigation + receipt style
- **Auth:** Cashier/operator roles
- **Key features:**
  - Fast intake form (POS-style)
  - Pricing by cloth type
  - QR code per ticket
  - Status chips (received → washing → ready → delivered)
  - Delivery route tracking
  - Payment history
  - PDF receipt generation
  - Daily cash report

---

## Phase Plan

### ✅ Phase 0: Setup
- [x] Roadmap yozildi
- [x] 3 papka yaratildi
- [x] TodoWrite tracking boshlandi

### 🔄 Phase 1: Parallel Build (3 ta agent parallel)
Har bir agent o'z loyihasini to'liq quradi:
1. Django project + apps yaratish
2. Models + migrations
3. Views + URL routing
4. HTMX bilan dynamic interactions
5. Tailwind CSS styling (loyihaga xos rang/font)
6. Templates (base + components + pages)
7. Admin customization
8. Sample data fixtures (seed script)
9. README.md (run instructions)
10. Verification: migrate + runserver test

### Phase 2: Verification
- Har loyihada `python manage.py check` chiqishini tekshirish
- `python manage.py migrate` ishlashini tekshirish
- `python manage.py runserver` ishga tushishini tekshirish
- Asosiy URL javob berishini tekshirish

### Phase 3: Final report
- Foydalanuvchiga xulosa
- Har loyiha uchun run instructions
- Screenshot/URL ro'yxati

---

## Acceptance Criteria (har loyiha uchun)

- ✅ `python manage.py check` xato bermaydi
- ✅ `python manage.py migrate` ishlaydi
- ✅ `python manage.py runserver` 8000-portda ishga tushadi
- ✅ Bosh sahifa (`/`) 200 status qaytaradi
- ✅ Admin panel (`/admin/`) ishlaydi (superuser: admin/admin123)
- ✅ Kamida 5 ta model bor
- ✅ Kamida 10 ta view bor
- ✅ Sample data 10+ yozuv bilan to'lgan
- ✅ README.md run instructions bilan mavjud
- ✅ Tailwind CSS to'g'ri yuklangan va loyiha-spec rang ishlaydi
- ✅ HTMX kamida 3 joyda ishlatilgan
- ✅ Tarmoq vizual ravishda boshqa 2 loyihadan butunlay farq qiladi
