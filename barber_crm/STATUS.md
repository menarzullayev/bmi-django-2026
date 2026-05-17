# Barber CRM — Статус сборки

**Статус:** ГОТОВ
**Дата сборки:** 2026-05-17
**Язык интерфейса:** Русский

## Результаты проверки

- `python manage.py check` — без ошибок
- `python manage.py makemigrations` — миграции созданы для всех 7 приложений
- `python manage.py migrate` — успешно
- `python manage.py seed_data` — создано: 15 клиентов, 33 записи, 20 услуг, 4 мастера
- HTTP smoke-тесты (порт 8765):
  - `GET /` → 200
  - `GET /services/` → 200
  - `GET /booking/` → 200
  - `GET /accounts/login/` → 200
  - `GET /accounts/register/` → 200
  - `GET /admin/login/` → 200
  - `GET /dashboard/` → 200 (после входа)
  - `GET /dashboard/queue/` → 200
  - `GET /dashboard/clients/` → 200
  - `GET /dashboard/schedule/` → 200
  - `GET /dashboard/services/` → 200
  - `GET /me/` → 200
  - `GET /me/loyalty/` → 200
  - `GET /booking/slots/?...` → 200 (HTMX)

## Команда запуска

```bash
cd /home/nsn/Django_projects/barber_crm
source venv/bin/activate
python manage.py runserver 8765
```

## Учётные данные

- Администратор: `admin` / `admin123`
- Мастер: `master1` / `master123` (также `master2`, `master3`, `master4`)
- Клиент: `client1` / `client123` (также `client2` … `client15`)
- Вход по телефону: код OTP — `123456` (выводится в консоль `runserver`)

## Карта URL

| URL | Назначение |
|-----|-----------|
| `/` | Главная (лендинг) |
| `/services/` | Каталог услуг с фильтром |
| `/services/<id>/` | Детали услуги |
| `/booking/` | Онлайн-запись |
| `/booking/slots/` | HTMX: свободное время |
| `/booking/confirm/<svc>/<barber>/<dt>/` | Подтверждение брони |
| `/booking/success/<id>/` | Успех |
| `/accounts/login/` | Вход (пароль + OTP-таб) |
| `/accounts/register/` | Регистрация |
| `/accounts/logout/` | Выход |
| `/me/` | Мои записи |
| `/me/loyalty/` | Баланс + история бонусов |
| `/me/loyalty/more/` | HTMX «Загрузить ещё» |
| `/dashboard/` | KPI-панель (для staff) |
| `/dashboard/schedule/` | Расписание недели |
| `/dashboard/queue/` | Живая очередь + HTMX-кнопки |
| `/dashboard/clients/` | Клиентская база с поиском |
| `/dashboard/services/` | Управление услугами |
| `/admin/` | Админка Django |

## БМР

- **Тема:** «Создание программного обеспечения для управления записями и клиентской базой парикмахерской»
- **Студент:** Журакулова Дилнавоз Мехриддин кизи
- **Группа:** DI-O22-04
- **Руководитель:** Убайдуллаев М.
