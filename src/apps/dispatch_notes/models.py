# src/apps/inventory/models.py
from django.db import models
from apps.inventory.models import Supplier
from apps.inventory.models import Product

class DispatchNote(models.Model):
    beneficiary = models.CharField(max_length=100)
    dispatch_date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    driver_id = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50)
    vehicle_color = models.CharField(max_length=30)
    license_plate = models.CharField(max_length=15)
    observations = models.TextField(blank=True)

    def update_product_stock_on_dispatch(self):
        """
        Actualiza el stock de los productos para todos los ítems de esta nota.
        """
        for item in self.dispatchitem_set.all():
            product = item.product
            product.current_stock -= item.quantity
            product.save()

class DispatchItem(models.Model):
    dispatch_note = models.ForeignKey(DispatchNote, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()