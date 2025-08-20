# src/apps/reception_notes/api_views.py
from rest_framework import viewsets
from .models import ReceptionNote, ReceptionItem
from .serializers import ReceptionNoteSerializer, ReceptionItemSerializer

class ReceptionNoteViewSet(viewsets.ModelViewSet):
    queryset = ReceptionNote.objects.all().order_by('-reception_number')
    serializer_class = ReceptionNoteSerializer

class ReceptionItemViewSet(viewsets.ModelViewSet):
    queryset = ReceptionItem.objects.all()
    serializer_class = ReceptionItemSerializer