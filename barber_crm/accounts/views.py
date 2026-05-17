from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from clients.models import Client

User = get_user_model()

OTP_CODE = '123456'


def login_view(request):
    error = None
    if request.method == 'POST':
        mode = request.POST.get('mode', 'password')
        if mode == 'otp':
            phone = (request.POST.get('phone') or '').strip()
            code = (request.POST.get('code') or '').strip()
            if not phone:
                error = 'Введите номер телефона'
            elif not code:
                print(f'OTP for {phone}: {OTP_CODE}')
                return render(request, 'accounts/login.html', {
                    'otp_sent': True,
                    'phone': phone,
                    'info': f'Код отправлен. Для входа используйте: {OTP_CODE}',
                })
            elif code == OTP_CODE:
                user = User.objects.filter(phone=phone).first()
                if user is None:
                    error = 'Пользователь с таким телефоном не найден'
                else:
                    login(request, user)
                    return redirect('clients:me')
            else:
                error = 'Неверный код'
        else:
            username = (request.POST.get('username') or '').strip()
            password = request.POST.get('password') or ''
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('clients:me' if not user.is_staff_role else 'core:dashboard')
            error = 'Неверный логин или пароль'
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('core:landing')


def register_view(request):
    error = None
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        password = request.POST.get('password') or ''
        if not (username and phone and password):
            error = 'Заполните логин, телефон и пароль'
        elif User.objects.filter(username=username).exists():
            error = 'Логин уже занят'
        elif User.objects.filter(phone=phone).exists():
            error = 'Этот телефон уже зарегистрирован'
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                role='client',
            )
            Client.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect('clients:me')
    return render(request, 'accounts/register.html', {'error': error})
