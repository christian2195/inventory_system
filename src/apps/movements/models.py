from django.db import models
from django.utils import timezone
from apps.inventory.models import Product
from django.contrib.auth.models import User

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    observations = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.get_movement_type_display()} de {self.quantity} {self.product.description}'

class Entry(models.Model):
    # This model might not be necessary if 'Movement' handles all types.
    # It's included here to match the view, but you might want to simplify later.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    # ... other fields