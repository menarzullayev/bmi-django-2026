from django import forms

from .models import WorkOrder


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            'vehicle', 'assigned_mechanic', 'status', 'priority',
            'problem_description', 'diagnosis_notes',
            'estimated_cost', 'expected_ready_at', 'mileage_at_intake',
        ]
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 4}),
            'diagnosis_notes': forms.Textarea(attrs={'rows': 3}),
            'expected_ready_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 '
            'text-sm shadow-sm focus:border-orange-500 focus:ring-orange-500'
        )
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {base}'.strip()
        # Order vehicles by display
        from vehicles.models import Vehicle
        self.fields['vehicle'].queryset = Vehicle.objects.select_related('customer').order_by('plate')
