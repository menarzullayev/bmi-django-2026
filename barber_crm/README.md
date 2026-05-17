# Барбершоп CRM

Веб-приложение для управления записями, услугами и клиентами парикмахерской. Дипломная работа (БМР).

## Описание

Система позволяет клиентам бронировать визиты онлайн, накапливать бонусные баллы и отслеживать историю посещений. Мастерам и администрации даёт панель управления: расписание, очередь, клиенты, услуги и аналитика.

## Технологии

- Python 3.12, Django 5
- SQLite
- Tailwind CSS (CDN), HTMX, Poppins
- Pillow, ReportLab, qrcode

## Установка

```bash
cd /home/nsn/Django_projects/barber_crm
python3 -m venv venv
source venv/bin/activate
pip install django pillow reportlab qrcode
```

## Запуск

```bash
source venv/bin/activate
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8765
```

Открыть в браузере: <http://127.0.0.1:8765/>

## Учётные данные

| Роль | Логин | Пароль |
|------|-------|--------|
| Администратор | `admin` | `admin123` |
| Мастер | `master1` … `master4` | `master123` |
| Клиент | `client1` … `client15` | `client123` |

OTP-код (вход по телефону): `123456`.

## Карта URL

| URL | Описание |
|-----|----------|
| `/` | Лендинг |
| `/services/` | Каталог услуг |
| `/services/<id>/` | Детальная страница услуги |
| `/booking/` | Запись |
| `/booking/slots/` | HTMX: свободные слоты |
| `/booking/confirm/.../` | Подтверждение |
| `/booking/success/<id>/` | Успешная запись |
| `/accounts/login/` | Вход |
| `/accounts/register/` | Регистрация |
| `/accounts/logout/` | Выход |
| `/me/` | Мои записи |
| `/me/loyalty/` | Программа лояльности |
| `/dashboard/` | Панель управления |
| `/dashboard/schedule/` | Расписание |
| `/dashboard/clients/` | Клиенты |
| `/dashboard/services/` | Управление услугами |
| `/dashboard/queue/` | Живая очередь |
| `/admin/` | Админка Django |

## Тема БМР

«Создание программного обеспечения для управления записями и клиентской базой парикмахерской».

## Студент

Журакулова Дилнавоз Мехриддин кизи · Группа DI-O22-04.

## Руководитель

Убайдуллаев М.
