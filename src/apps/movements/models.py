# src/apps/movements/models.py
from django.db import models
from apps.inventory.models import Product  # Asegúrate de importar Product
from django.utils import timezone

class MovementManager(models.Manager):
    def get_daily_movements(self, movement_type='IN'):
        today = timezone.now().date()
        return self.get_queryset().filter(
            movement_type=movement_type,
            date__date=today
        ).count()

class Entry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    # Otros campos relacionados a la entrada, si los hay
    def __str__(self):
        return f"Entrada de {self.quantity} de {self.product}"

class Movement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    )
    
    # Aquí puedes usar el campo `entry` como un OneToOneField si cada movimiento se relaciona con una única entrada,
    # o un ForeignKey si un movimiento puede tener múltiples entradas. Basado en el código actual, parece ser un ForeignKey.
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True)
    movement_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivered_to = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    observations = models.TextField(blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    objects = MovementManager()

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        product = self.product
        if self.movement_type == 'IN':
            product.current_stock += self.quantity
        else:
            product.current_stock -= self.quantity
        product.save()
        
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.description} ({self.quantity})"