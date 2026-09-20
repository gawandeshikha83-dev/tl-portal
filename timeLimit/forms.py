from django import forms
from .models import TimeLimit


class TimeLimitForm(forms.ModelForm):

    class Meta:
        model = TimeLimit

        fields = [
            'sno',
            'tl_no',
            'received_date',
            'sender_name',
            'letter_no_date',
            'subject',
            'section_name',
            'description',
            'current_status',
            'tl_pdf',
            'answer_pdf',
        ]

        widgets = {

            'sno': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'स.क्र.'
            }),

            'tl_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'TL No.'
            }),

            'received_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'sender_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'प्रेषक'
            }),

            'letter_no_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'क्र/दिनांक'
            }),

            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'विषय'
            }),

            'section_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'संबंधित शाखा का नाम'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'विवरण',
                'rows': 4
            }),

            'current_status': forms.Select(attrs={
                'class': 'form-control'
            }),

            'tl_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),

            'answer_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
        }