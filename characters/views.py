from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import Character
from .serializers import CharacterListSerializer, CharacterDetailSerializer, CharacterSearchSeializer
from .services import SemanticSearchService


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

@api_view(['GET'])
def semantic_search_characters(request):
    """Perform semantic search on characters

    GET /api/characters/search?query=<search_term>&limit=<number>
    """
    serializer = CharacterSearchSeializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    limit = serializer.validated_data.get('limit', 5)

    try:
        search_service = SemanticSearchService()
        print(f"Performing semantic search for query: '{query}' with limit {limit}")

        characters = search_service.search_characters(query, limit)

        print(f"Semantic search results for query '{query}': {len(characters)} characters found")

        # Serialize the results
        character_serializer = CharacterListSerializer(characters, many=True)

        return Response({
            "query": query,
            "results_count": len(characters),
            "results": character_serializer.data

        })

    except ValueError as e:
        print(f"Search service error: {e}")
        return Response(
            {"error": "Search service not available. Please try again later."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {"error": f"Search failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

