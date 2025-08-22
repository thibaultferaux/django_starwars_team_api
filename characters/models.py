from django.db import models

from core.models import SoftDeleteModel


class Character(SoftDeleteModel):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    height = models.FloatField(null=True, blank=True)
    mass = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    homeworld = models.CharField(max_length=100, null=True, blank=True)
    species = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)

    # Affiliations (stored as JSON)
    affiliations_data = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def affiliations(self):
        """Return a list of affiliations."""
        return self.affiliations_data if self.affiliations_data else []


class Master(SoftDeleteModel):
    """Model to store master-apprentice relationships."""
    character = models.ForeignKey(
        Character,
        related_name='masters',
        on_delete=models.CASCADE,
    )
    master_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('character', 'master_name')

    def __str__(self):
        return f"{self.character.name} - Master: {self.master_name}"


