from django.urls import path
from .views import CharacterListView, CharacterDetailView

urlpatterns = [
    path('', CharacterListView.as_view(), name='character-list'),
    path('<int:id>/', CharacterDetailView.as_view(), name='character-detail'),
]
