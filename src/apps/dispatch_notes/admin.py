from django.contrib import admin
from .models import DispatchNote, DispatchItem

class DispatchItemInline(admin.TabularInline):
    model = DispatchItem
    extra = 1

@admin.register(DispatchNote)
class DispatchNoteAdmin(admin.ModelAdmin):
    list_display = ('beneficiary', 'dispatch_date', 'supplier', 'order_number')
    list_filter = ('dispatch_date', 'supplier')
    search_fields = ('beneficiary', 'order_number')
    inlines = [DispatchItemInline]