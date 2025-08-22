from rest_framework import generics
from django.db.models import Q

from .models import Character
from .serializers import CharacterListSerializer, CharacterDetailSerializer


class CharacterListView(generics.ListAPIView):
    """List all Star Wars characters with filtering"""
    queryset = Character.objects.all()
    serializer_class = CharacterListSerializer
    ordering = ['name']

    def get_queryset(self):
        """Custom queryset with search functionality."""
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(species__icontains=search) |
                Q(homeworld__icontains=search)
            )

        return queryset

class CharacterDetailView(generics.RetrieveAPIView):
    """Retrieve detailed information about a specific character"""
    queryset = Character.objects.all()
    serializer_class = CharacterDetailSerializer
    lookup_field = 'id'
