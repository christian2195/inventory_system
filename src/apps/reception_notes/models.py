# src/apps/reception_notes/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Supplier
from django.contrib.auth.models import User # <-- CAMBIA ESTA LÍNEA

class ReceptionNote(models.Model):
    RECEPTION_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('VALIDATED', 'Validada'),
        ('CANCELLED', 'Cancelada'),
    ]

    reception_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    reception_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # <-- CAMBIA ESTA LÍNEA
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RECEPTION_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'Nota de Recepción #{self.reception_number}'

class ReceptionItem(models.Model):
    reception_note = models.ForeignKey(ReceptionNote, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.description} - {self.quantity}'