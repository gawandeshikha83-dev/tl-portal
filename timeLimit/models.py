from django.db import models


class TimeLimit(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Disposed', 'Disposed'),
    ]

    sno = models.PositiveIntegerField(
        verbose_name='स.क्र.'
    )

    tl_no = models.CharField(
        max_length=100,
        verbose_name='TL No.'
    )

    received_date = models.DateField(
        verbose_name='प्राप्ति दिनांक'
    )

    sender_name = models.CharField(
        max_length=200,
        verbose_name='प्रेषक'
    )

    letter_no_date = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='क्र/दिनांक'
    )

    subject = models.CharField(
        max_length=300,
        verbose_name='विषय',
        blank=True
    )

    section_name = models.CharField(
        max_length=200,
        verbose_name='संबंधित शाखा का नाम'
    )

    description = models.TextField(
        verbose_name='विवरण',
        blank=True
    )

    current_situation = models.TextField(
        blank=True,
        default='',
        verbose_name='वर्तमान स्थिति'
    )

    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name='स्थिति'
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.tl_no