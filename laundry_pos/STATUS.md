# Химчистка POS — Статус сборки

**Статус:** ГОТОВ
**Дата сборки:** 2026-05-17
**Язык интерфейса:** Русский

## Результаты проверки

- `python manage.py check` — OK (0 issues)
- `python manage.py makemigrations` — OK (созданы initial для accounts, customers, catalog, intake, payments, delivery)
- `python manage.py migrate` — OK
- `python manage.py seed_data` — OK
  - Пользователей: 6
  - Клиентов: 30
  - Видов одежды: 12
  - Услуг: 6
  - Прайсов: 72
  - Квитанций: 50
  - Вещей: 208
  - Оплат: 27
  - Маршрутов доставки: 5

## HTTP smoke-тесты (порт 8767)

Анонимные запросы:

| URL                        | Код  | Комментарий                  |
|----------------------------|------|------------------------------|
| `/`                        | 302  | редирект на /login/          |
| `/login/`                  | 200  | страница входа               |
| `/admin/login/`            | 200  | админка                      |
| `/pos/`                    | 302  | требует входа                |
| `/tickets/`                | 302  | требует входа                |
| `/intake/new/`             | 302  | требует входа                |
| `/pricing/`                | 302  | требует входа                |
| `/delivery/`               | 302  | требует входа                |
| `/payments/`               | 302  | требует входа                |
| `/reports/daily/`          | 302  | требует входа                |
| `/qr/T-20260517-0041/`     | 200  | публично, без авторизации    |

Под логином admin:

| URL                                | Код |
|------------------------------------|-----|
| `/pos/`                            | 200 |
| `/tickets/`                        | 200 |
| `/intake/new/`                     | 200 |
| `/pricing/`                        | 200 |
| `/delivery/`                       | 200 |
| `/payments/`                       | 200 |
| `/reports/daily/`                  | 200 |
| `/catalog/cloth-types/`            | 200 |
| `/catalog/service-types/`          | 200 |
| `/delivery/route/new/`             | 200 |
| `/tickets/41/`                     | 200 |
| `/tickets/41/receipt/`             | 200 |
| `/tickets/41/receipt/pdf/`         | 200 |
| `POST /intake/new/`                | 302 (создана квитанция T-20260517-0051) |
| `GET /pricing/cell/1/1/edit/`      | 200 |
| `POST /pricing/cell/1/1/save/`     | 200 |

Все запросы — 200 или 302. Пятисотых нет.

## Команда запуска

```bash
cd /home/nsn/Django_projects/laundry_pos
source venv/bin/activate
python manage.py runserver 8767
```

## Учётные данные

- `admin` / `admin123` — администратор (superuser)
- `cashier1` / `admin123` — кассир
- `cashier2` / `admin123` — кассир
- `operator` / `admin123` — оператор
- `driver1` / `admin123` — водитель
- `driver2` / `admin123` — водитель

## Демо QR

<http://127.0.0.1:8767/qr/T-20260517-0041/>

(Откройте любую квитанцию в админке или на `/tickets/` и скачайте/отсканируйте её QR.)

## Карта URL

- `/` — корень (редирект)
- `/login/`, `/logout/`
- `/admin/` — Django-админка
- `/pos/` — POS-дашборд
- `/intake/new/` — приём заказа
- `/intake/customer/search/` — HTMX поиск клиента
- `/intake/garment/add/` — HTMX добавить строку вещи
- `/intake/price/` — HTMX автозаполнение цены
- `/tickets/` — список квитанций (фильтры)
- `/tickets/<pk>/` — детали
- `/tickets/<pk>/receipt/` — чек (HTML)
- `/tickets/<pk>/receipt/pdf/` — чек (PDF 80мм, DejaVuSans)
- `/tickets/<pk>/status/` — смена статуса (HTMX POST)
- `/tickets/<pk>/pay/` — приём оплаты (POST)
- `/tickets/by-number/<ticket_number>/` — поиск по номеру
- `/pricing/` — матрица прайс-листа (HTMX inline edit)
- `/pricing/cell/<cloth_id>/<service_id>/edit/`
- `/pricing/cell/<cloth_id>/<service_id>/save/`
- `/catalog/cloth-types/`, `/catalog/service-types/`
- `/delivery/` — список маршрутов
- `/delivery/route/new/` — создать маршрут
- `/delivery/route/<pk>/` — детали маршрута
- `/delivery/assignment/<pk>/deliver/` — отметить доставлено (HTMX POST)
- `/payments/` — история оплат
- `/reports/daily/` — отчёт за день
- `/qr/<ticket_number>/` — публичная страница статуса (без авторизации)

## БМР

- **Тема:** «Разработка программного обеспечения для учёта заказов и клиентов в химчистке»
- **Студент:** Примова Дилноза Хужамшукуровна
- **Группа:** DI-O22-04
- **Руководитель:** Убайдуллаев М.
