from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from characters.models import Character
from core.models import SoftDeleteModel


class Team(SoftDeleteModel):
    """Model representing a Star Wars team."""
    name = models.CharField(max_length=200, unique=True, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams', null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Team constraints
    MAX_MEMBERS = 5

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.team_members.count()}/{self.MAX_MEMBERS} members)"

    def clean(self):
        """Validate team contraints."""
        if self.pk: # Only validate if the team already exists
            current_members = self.team_members.count()
            if current_members > self.MAX_MEMBERS:
                raise ValueError(f"Team cannot have more than {self.MAX_MEMBERS} members. Current members: {current_members}")

            # Check for evil members
            evil_members = self.members.filter(is_evil=True)
            if evil_members.exists():
                evil_names = ", ".join([member.name for member in evil_members])
                raise ValidationError(f"Team cannot contain evil members: {evil_names}")

    def can_add_member(self, character):
        """Check if a character can be added to the team"""
        if self.members.count() >= self.MAX_MEMBERS:
            return False, f"Team is full ({self.MAX_MEMBERS} members max)."

        if character.is_evil:
            return False, f"{character.name} is evil and cannot join the team."

        if self.members.filter(id=character.id).exists():
            return False, f"{character.name} is already a member of the team."

        return True, f"{character.name} can join the team."

    def add_member(self, character):
        """Add a character to the team with validation"""
        can_add, message = self.can_add_member(character)
        if not can_add:
            raise ValidationError(message)

        team_member = TeamMember.objects.create(team=self, character=character)
        return team_member

    def remove_member(self, character):
        """Remove a character from the team"""
        try:
            team_member = TeamMember.objects.get(team=self, character=character)
            team_member.delete()
            return True
        except TeamMember.DoesNotExist:
            return False

    @property
    def is_full(self):
        """Check if team is at maximum capacity."""
        return self.team_members.count() >= self.MAX_MEMBERS

    @property
    def average_evilness_score(self):
        """Calculate the average evilness score of team members."""
        members = self.members.all()
        if not members:
            return 0

        total_score = sum(member.evilness_score for member in members)
        return round(total_score / len(members))

class TeamMember(SoftDeleteModel):
    """Many-to-many relationship between teams and characters."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='team_memberships')

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'character')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.character.name} in {self.team.name}"

# Add related name to Character model for easy access
Team.add_to_class('members', models.ManyToManyField(
    Character,
    through='TeamMember',
    related_name='teams',
    blank=True,
))

