"""
URL configuration for django_starwars_team_api project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/characters/', include('characters.urls')),
    path('api/teams/', include('teams.urls')),
]
