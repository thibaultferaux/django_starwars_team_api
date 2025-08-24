from django.urls import path

from .views import (
    TeamListCreateView,
    TeamDetailView,
    add_member,
    remove_member,
)

urlpatterns = [
    path('', TeamListCreateView.as_view(), name='team-list-create'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('<int:team_id>/add-member/', add_member, name='team-add-member'),
    path('<int:team_id>/remove-member/', remove_member, name='team-remove-member'),
]