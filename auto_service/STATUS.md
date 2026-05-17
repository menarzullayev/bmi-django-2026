# Автосервис ERP — Статус сборки

**Статус:** ГОТОВ
**Дата сборки:** 2026-05-17
**Язык интерфейса:** Русский

## Результаты проверки
- `python manage.py check` — OK (0 issues)
- `makemigrations` + `migrate` — OK
- `seed_data` — OK (admin, reception, 4 механика, 25 клиентов, 35 авто, 162 запчасти, 40 заказов, 6 счетов)
- HTTP smoke-тесты на порту 8766:
  - `GET /` → 302 (редирект на /dashboard/)
  - `GET /login/` → 200
  - `GET /admin/login/` → 200
  - `GET /dashboard/` → 302 (без сессии), 200 (с сессией)
  - `GET /orders/` → 302, 200
  - `GET /kanban/` → 302, 200
  - `GET /parts/` → 302, 200
  - `GET /mechanics/` → 302, 200
  - `GET /customers/` → 302, 200
  - `GET /vehicles/` → 302, 200
  - `GET /invoices/` → 302, 200
  - `GET /reports/` → 302, 200
  - `GET /orders/<id>/` → 200
  - `GET /invoices/<id>/` → 200
  - `GET /invoices/<id>/pdf/` → 200 (PDF, 28 КБ)

## Команда запуска

```bash
cd /home/nsn/Django_projects/auto_service
source venv/bin/activate
python manage.py runserver 8766
```

## Учётные данные

- Администратор: `admin` / `admin123`
- Приёмщик:      `reception` / `admin123`
- Механик:       `mechanic1` / `admin123` (также `mechanic2`, `mechanic3`, `mechanic4`)

## Карта URL

| URL | Назначение |
|-----|-----------|
| `/` | Редирект на дашборд |
| `/login/`, `/logout/` | Авторизация |
| `/admin/` | Админ-панель Django |
| `/dashboard/` | KPI-дашборд (Активные заказы, Выручка, Готово, Низкие остатки) + Chart.js |
| `/orders/` | Список заказ-нарядов с фильтрами по статусу, приоритету, механику |
| `/orders/new/` | Создание заказ-наряда |
| `/orders/<id>/` | Карточка заказа: работы, запчасти, статус-таймлайн |
| `/orders/<id>/transition/` | POST/HTMX смена статуса (поддерживает kanban-режим) |
| `/orders/<id>/tasks/add/` | HTMX добавление работы (вставка строки таблицы) |
| `/orders/<id>/parts/add/` | Добавление запчасти со списанием со склада |
| `/kanban/` | Канбан-доска со столбцами по статусам + HTMX «Далее» |
| `/parts/` | Склад с HTMX +/- остатков, бейдж низкого уровня |
| `/parts/new/` | Создание запчасти |
| `/parts/<id>/` | Карточка с историей использования |
| `/parts/<id>/adjust/` | HTMX корректировка остатка |
| `/mechanics/` | Загрузка механиков (активные, завершено, часы) |
| `/mechanics/<id>/` | Профиль и список заказов |
| `/customers/` | Список клиентов |
| `/customers/<id>/` | Карточка клиента с авто и историей заказов |
| `/vehicles/` | Список автомобилей |
| `/invoices/` | Список счетов |
| `/invoices/<id>/` | Печатная HTML-карточка счёта |
| `/invoices/<id>/pdf/` | PDF-счёт (ReportLab + DejaVuSans, A4) |
| `/reports/` | Дневной отчёт (7 дней) + по механикам |

## HTMX-функции (≥3)

1. **Канбан «Далее»** — `partials/kanban_card.html` POST в `/orders/<id>/transition/` с `from=kanban`, ответ заменяет карточку.
2. **Корректировка склада** — кнопки +/− в `partials/parts_row.html` POST в `/parts/<id>/adjust/`, ответ заменяет строку.
3. **Добавление работы** — форма в `orders/detail.html` POST в `/orders/<id>/tasks/add/`, ответ `beforeend` в `#tasks-tbody`.

## БМР

- Тема: «Создание системы управления заказами и клиентской базой в автосервисе»
- Студент: Бахронкулов Шодиёр Ирисбой ўғли
- Группа: DI-O22-04
- Руководитель: Убайдуллаев М.
