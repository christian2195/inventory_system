# src/apps/dispatch_notes/admin.py
from django.contrib import admin
from .models import DispatchNote, DispatchItem

class DispatchItemInline(admin.TabularInline):
    model = DispatchItem
    extra = 1

@admin.register(DispatchNote)
class DispatchNoteAdmin(admin.ModelAdmin):
    list_display = (
        'dispatch_number',
        'client',
        'dispatch_date',
        'status',
        'beneficiary', # <-- AÑADIDO
        'supplier',    # <-- AÑADIDO
        'order_number',# <-- AÑADIDO
        'driver_name', # <-- AÑADIDO
        'license_plate'# <-- AÑADIDO
    )
    list_filter = ('dispatch_date', 'status', 'client')
    search_fields = ('dispatch_number', 'client__name', 'notes')
    inlines = [DispatchItemInline]