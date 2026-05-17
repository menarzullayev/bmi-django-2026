import io
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as units_mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import IntakeTicket, STATUS_CHOICES
from payments.models import Payment


@login_required
def ticket_list(request):
    qs = IntakeTicket.objects.select_related('customer', 'cashier').all()
    status = request.GET.get('status', '').strip()
    phone = request.GET.get('phone', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if status:
        qs = qs.filter(status=status)
    if phone:
        qs = qs.filter(customer__phone__icontains=phone)
    if date_from:
        qs = qs.filter(received_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(received_at__date__lte=date_to)

    return render(request, 'tickets/list.html', {
        'tickets': qs[:200],
        'status_choices': STATUS_CHOICES,
        'filters': {
            'status': status, 'phone': phone,
            'date_from': date_from, 'date_to': date_to,
        },
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(
        IntakeTicket.objects.select_related('customer', 'cashier').prefetch_related(
            'garments__cloth_type', 'garments__service_type', 'payments__cashier'
        ),
        pk=pk,
    )
    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'status_choices': STATUS_CHOICES,
    })


@login_required
def ticket_by_number(request, ticket_number):
    ticket = get_object_or_404(IntakeTicket, ticket_number=ticket_number)
    return redirect('tickets:detail', pk=ticket.pk)


@login_required
def ticket_receipt(request, pk):
    ticket = get_object_or_404(
        IntakeTicket.objects.select_related('customer', 'cashier').prefetch_related(
            'garments__cloth_type', 'garments__service_type', 'payments'
        ),
        pk=pk,
    )
    return render(request, 'tickets/receipt.html', {'ticket': ticket})


@login_required
@require_POST
def ticket_status_change(request, pk):
    ticket = get_object_or_404(IntakeTicket, pk=pk)
    new_status = request.POST.get('status')
    valid = {c[0] for c in STATUS_CHOICES}
    if new_status in valid:
        ticket.status = new_status
        now = timezone.now()
        if new_status == 'ready' and not ticket.ready_at:
            ticket.ready_at = now
        if new_status == 'delivered' and not ticket.delivered_at:
            ticket.delivered_at = now
        ticket.save(update_fields=['status', 'ready_at', 'delivered_at'])
        ticket.garments.update(status=new_status)

    if request.headers.get('HX-Request'):
        return render(request, 'partials/ticket_status_chip.html', {'ticket': ticket, 'status_choices': STATUS_CHOICES})
    return redirect('tickets:detail', pk=pk)


@login_required
def ticket_pay(request, pk):
    ticket = get_object_or_404(IntakeTicket, pk=pk)
    if request.method == 'POST':
        try:
            amount = Decimal(str(request.POST.get('amount', '0')).replace(',', '.'))
        except Exception:
            amount = Decimal('0')
        method = request.POST.get('method', 'cash')
        note = request.POST.get('note', '').strip()
        if amount > 0:
            Payment.objects.create(
                ticket=ticket, amount=amount, method=method,
                cashier=request.user, note=note,
            )
            ticket.amount_paid = sum((p.amount for p in ticket.payments.all()), Decimal('0'))
            ticket.customer.total_spent = (ticket.customer.total_spent or Decimal('0')) + amount
            ticket.customer.save(update_fields=['total_spent'])
            ticket.save(update_fields=['amount_paid'])
            messages.success(request, f'Оплата {amount} принята.')
        else:
            messages.error(request, 'Сумма оплаты должна быть больше нуля.')
        return redirect('tickets:detail', pk=pk)
    return render(request, 'tickets/detail.html', {'ticket': ticket, 'status_choices': STATUS_CHOICES})


@login_required
def ticket_receipt_pdf(request, pk):
    ticket = get_object_or_404(
        IntakeTicket.objects.select_related('customer', 'cashier').prefetch_related(
            'garments__cloth_type', 'garments__service_type', 'payments'
        ),
        pk=pk,
    )

    # Register a Cyrillic-capable font (DejaVuSans is bundled with most Linux installs)
    font_name = 'Helvetica'
    for candidate in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
    ]:
        try:
            pdfmetrics.registerFont(TTFont('DejaVu', candidate))
            font_name = 'DejaVu'
            break
        except Exception:
            continue

    width = 80 * mm
    line_h = 4.2 * mm
    margin = 4 * mm

    garments = list(ticket.garments.all())
    payments = list(ticket.payments.all())
    rows_estimate = 18 + len(garments) * 2 + len(payments)
    height = max(120 * mm, rows_estimate * line_h + 20 * mm)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    y = height - margin

    def write(text, font=None, size=9, dy=None, bold=False):
        nonlocal y
        c.setFont(font or (font_name + ('-Bold' if bold and font_name == 'Helvetica' else '')), size)
        c.drawString(margin, y, text)
        y -= (dy or line_h)

    def write_kv(left, right, size=9, bold=False):
        nonlocal y
        c.setFont(font_name + ('-Bold' if bold and font_name == 'Helvetica' else ''), size)
        c.drawString(margin, y, left)
        c.drawRightString(width - margin, y, right)
        y -= line_h

    def divider():
        nonlocal y
        c.setDash(1, 2)
        c.line(margin, y, width - margin, y)
        c.setDash()
        y -= line_h * 0.7

    write('ХИМЧИСТКА POS', size=12, bold=True, dy=line_h * 1.2)
    write('Квитанция-чек', size=8)
    divider()
    write(f'№ {ticket.ticket_number}', size=11, bold=True)
    write(f'Принято: {timezone.localtime(ticket.received_at).strftime("%d.%m.%Y %H:%M")}', size=8)
    write(f'Кассир: {ticket.cashier.display_name() if hasattr(ticket.cashier, "display_name") else ticket.cashier}', size=8)
    divider()
    write(f'Клиент: {ticket.customer.full_name}', size=9)
    write(f'Тел.: {ticket.customer.phone}', size=8)
    if ticket.pickup_method == 'delivery' and ticket.delivery_address:
        write(f'Доставка: {ticket.delivery_address[:40]}', size=8)
    divider()
    write('ВЕЩИ:', size=9, bold=True)
    for g in garments:
        write_kv(f'{g.cloth_type.name} — {g.service_type.name}', f'{g.price:.2f}', size=8)
        meta = ' '.join([s for s in [g.color, g.brand] if s])
        if meta:
            write(f'   {meta[:36]}', size=7)
    divider()
    write_kv('Подытог:', f'{ticket.subtotal:.2f}', size=9)
    if ticket.discount and ticket.discount > 0:
        write_kv('Скидка:', f'-{ticket.discount:.2f}', size=9)
    write_kv('ИТОГО:', f'{ticket.total:.2f}', size=11, bold=True)
    write_kv('Оплачено:', f'{ticket.amount_paid:.2f}', size=9)
    balance = ticket.total - ticket.amount_paid
    write_kv('К доплате:', f'{balance:.2f}', size=9, bold=True)
    divider()
    if payments:
        write('Оплаты:', size=8, bold=True)
        for p in payments:
            write_kv(f'{timezone.localtime(p.paid_at).strftime("%d.%m %H:%M")} {p.get_method_display()}', f'{p.amount:.2f}', size=8)
        divider()
    write(f'Статус: {ticket.get_status_display()}', size=9, bold=True)
    if ticket.ready_by:
        write(f'Готово к: {timezone.localtime(ticket.ready_by).strftime("%d.%m.%Y %H:%M")}', size=8)
    divider()

    # QR
    if ticket.qr_image:
        try:
            qr_size = 28 * mm
            c.drawImage(ticket.qr_image.path, (width - qr_size) / 2, y - qr_size,
                        width=qr_size, height=qr_size, preserveAspectRatio=True, mask='auto')
            y -= qr_size + 2 * mm
        except Exception:
            pass

    write('Спасибо за заказ!', size=9, bold=True)
    write('Тел. химчистки: +998 71 123-45-67', size=7)

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()

    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="receipt-{ticket.ticket_number}.pdf"'
    return resp
