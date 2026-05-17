from django.conf import settings


def bmi_metadata(request):
    return {
        'BMI': getattr(settings, 'BMI_METADATA', {}),
    }
