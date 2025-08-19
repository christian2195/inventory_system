from django.db import models
from apps.inventory.models import Product

class Entry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

class Movement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    )
    
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    movement_number = models.CharField(max_length=20, unique=True)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)  # ¡Solo una vez!
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivered_to = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    observations = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        product = self.product
        if self.movement_type == 'IN':
            product.current_stock += self.quantity
        else:
            product.current_stock -= self.quantity
        product.save()

class DispatchItem(models.Model):
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Item de Despacho"
        verbose_name_plural = "Items de Despacho"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} - {self.quantity} unidades"
class DispatchNote(models.Model):
    date = models.DateField()
    reference = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Despacho {self.reference} - {self.date}"