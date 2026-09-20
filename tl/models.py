from django.db import models


class TimeLimit(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Disposed', 'Disposed'),
    ]

    sno = models.PositiveIntegerField(verbose_name='S.No')
    tl_no = models.CharField(max_length=100, verbose_name='TL No')
    received_date = models.DateField(verbose_name='Received Date')
    sender_name = models.CharField(max_length=200, verbose_name='Sender Name')
    letter_date = models.DateField(verbose_name='Letter Date')
    section_name = models.CharField(max_length=200, verbose_name='Section Name')
    description = models.TextField(verbose_name='Description')

    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name='Current Status'
    )

    tl_pdf = models.FileField(
        upload_to='tl_pdfs/',
        blank=True,
        null=True,
        verbose_name='TL PDF'
    )

    answer_pdf = models.FileField(
        upload_to='answer_pdfs/',
        blank=True,
        null=True,
        verbose_name='Answer PDF'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tl_no