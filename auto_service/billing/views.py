import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from .models import Invoice


FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_PATH_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_PDF_FONT_REGISTERED = False


def _ensure_pdf_font():
    global _PDF_FONT_REGISTERED
    if _PDF_FONT_REGISTERED:
        return True
    if not os.path.exists(FONT_PATH):
        return False
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
        if os.path.exists(FONT_PATH_BOLD):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', FONT_PATH_BOLD))
        _PDF_FONT_REGISTERED = True
        return True
    except Exception:
        return False


@login_required
def invoice_list(request):
    q = (request.GET.get('q') or '').strip()
    paid = request.GET.get('paid') or ''
    qs = Invoice.objects.select_related(
        'workorder', 'workorder__vehicle__customer',
    )
    if q:
        qs = qs.filter(
            Q(invoice_number__icontains=q)
            | Q(workorder__order_number__icontains=q)
            | Q(workorder__vehicle__customer__name__icontains=q)
        )
    if paid == 'yes':
        qs = qs.filter(paid_at__isnull=False)
    elif paid == 'no':
        qs = qs.filter(paid_at__isnull=True)

    qs = qs.order_by('-issued_at')

    context = {
        'invoices': qs[:200],
        'total': qs.count(),
        'filter_q': q,
        'filter_paid': paid,
        'active_nav': 'invoices',
        'page_title': 'Счета',
    }
    return render(request, 'invoices/list.html', context)


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related(
            'workorder', 'workorder__vehicle__customer', 'workorder__assigned_mechanic',
        ),
        pk=pk,
    )
    order = invoice.workorder
    tasks = order.tasks.all()
    part_usages = order.part_usages.select_related('part').all()
    context = {
        'invoice': invoice,
        'order': order,
        'tasks': tasks,
        'part_usages': part_usages,
        'active_nav': 'invoices',
        'page_title': invoice.invoice_number,
    }
    return render(request, 'invoices/detail.html', context)


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related(
            'workorder', 'workorder__vehicle__customer', 'workorder__assigned_mechanic',
        ),
        pk=pk,
    )

    if not _ensure_pdf_font():
        # Fallback: render the print-friendly HTML page
        return invoice_detail(request, pk)

    order = invoice.workorder
    customer = order.vehicle.customer
    vehicle = order.vehicle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=str(invoice),
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        'H1', parent=styles['Heading1'], fontName='DejaVuSans',
        fontSize=18, spaceAfter=4,
    )
    h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'], fontName='DejaVuSans',
        fontSize=12, spaceAfter=2,
    )
    body = ParagraphStyle(
        'Body', parent=styles['Normal'], fontName='DejaVuSans',
        fontSize=10, leading=13,
    )
    small = ParagraphStyle(
        'Small', parent=styles['Normal'], fontName='DejaVuSans',
        fontSize=8, leading=10, textColor=colors.grey,
    )

    story = []
    story.append(Paragraph('АвтоСервис ERP', h1))
    story.append(Paragraph('Счёт на оплату услуг автосервиса', body))
    story.append(Spacer(1, 6))

    header_table = Table([
        [
            Paragraph(f'<b>Счёт №:</b> {invoice.invoice_number}', body),
            Paragraph(f'<b>Дата:</b> {invoice.issued_at.strftime("%d.%m.%Y")}', body),
        ],
        [
            Paragraph(f'<b>Заказ-наряд:</b> {order.order_number}', body),
            Paragraph(f'<b>Статус:</b> {invoice.status_label}', body),
        ],
    ], colWidths=[90 * mm, 90 * mm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph('Клиент', h2))
    story.append(Paragraph(
        f'{customer.name}<br/>Телефон: {customer.phone or "—"}<br/>'
        f'Email: {customer.email or "—"}<br/>Адрес: {customer.address or "—"}',
        body,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Автомобиль', h2))
    story.append(Paragraph(
        f'{vehicle.make} {vehicle.model} {vehicle.year}<br/>'
        f'Гос. номер: {vehicle.plate}<br/>'
        f'VIN: {vehicle.vin or "—"}<br/>'
        f'Пробег: {vehicle.mileage_km} км',
        body,
    ))
    story.append(Spacer(1, 10))

    # Tasks (labor)
    story.append(Paragraph('Выполненные работы', h2))
    tasks = list(order.tasks.all())
    if tasks:
        data = [['#', 'Описание', 'Часы', 'Ставка', 'Сумма']]
        for i, t in enumerate(tasks, 1):
            hours = t.actual_hours or t.estimated_hours
            data.append([
                str(i),
                t.description,
                f'{hours}',
                f'{t.hourly_rate}',
                f'{t.line_total:.2f}',
            ])
        tbl = Table(data, colWidths=[10 * mm, 100 * mm, 20 * mm, 25 * mm, 25 * mm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph('— нет работ —', body))
    story.append(Spacer(1, 8))

    # Parts
    story.append(Paragraph('Использованные запчасти', h2))
    usages = list(order.part_usages.select_related('part').all())
    if usages:
        data = [['#', 'Запчасть', 'Артикул', 'Кол-во', 'Цена', 'Сумма']]
        for i, u in enumerate(usages, 1):
            data.append([
                str(i),
                u.part.name,
                u.part.sku,
                str(u.quantity),
                f'{u.unit_price}',
                f'{u.line_total:.2f}',
            ])
        tbl = Table(data, colWidths=[10 * mm, 70 * mm, 30 * mm, 20 * mm, 25 * mm, 25 * mm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph('— запчасти не использовались —', body))
    story.append(Spacer(1, 10))

    # Totals
    totals_data = [
        ['Работы:', f'{order.labor_total:.2f} сум'],
        ['Запчасти:', f'{order.parts_total:.2f} сум'],
        ['Сумма без НДС:', f'{invoice.subtotal:.2f} сум'],
        ['НДС:', f'{invoice.tax_amount:.2f} сум'],
        ['ИТОГО:', f'{invoice.total:.2f} сум'],
    ]
    totals = Table(totals_data, colWidths=[120 * mm, 60 * mm])
    totals.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 1.0, colors.black),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    story.append(totals)
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        'Подпись приёмщика: ___________________________   '
        'Подпись клиента: ___________________________',
        body,
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        'АвтоСервис ERP — дипломная работа. '
        'Студент: Бахронкулов Шодиёр Ирисбой ўғли · Группа DI-O22-04.',
        small,
    ))

    doc.build(story)
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=False,
        filename=f'{invoice.invoice_number}.pdf',
        content_type='application/pdf',
    )
