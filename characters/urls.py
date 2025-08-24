from django.urls import path
from .views import CharacterListView, CharacterDetailView, semantic_search_characters

urlpatterns = [
    path('', CharacterListView.as_view(), name='character-list'),
    path('<int:id>/', CharacterDetailView.as_view(), name='character-detail'),
    path('search/', semantic_search_characters, name='character-search'),
]
