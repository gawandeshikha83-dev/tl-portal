from django.contrib import admin
from .models import TimeLimit


@admin.register(TimeLimit)
class TimeLimitAdmin(admin.ModelAdmin):

    list_display = (
        'sno',
        'tl_no',
        'subject',
        'received_date',
        'sender_name',
        'section_name',
        'current_status',
    )

    list_filter = (
        'current_status',
        'section_name',
        'received_date',
    )

    search_fields = (
        'tl_no',
        'subject',
        'sender_name',
        'section_name',
        'description',
    )

    ordering = ('sno',)

    list_per_page = 25