from rest_framework import serializers

from .models import Team, TeamMember
from characters.serializers import CharacterListSerializer
from characters.models import Character


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team member information."""
    character = CharacterListSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'character', 'joined_at']

class TeamListSerializer(serializers.ModelSerializer):
    """Serializer for team list view"""
    member_count = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)


    class Meta:
        model = Team
        fields = ['id', 'name', 'member_count', 'is_full', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

class TeamDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed team information"""
    members = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)
    average_evilness_score = serializers.IntegerField(read_only=True)
    team_stats = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'members', 'member_count',
            'is_full', 'average_evilness_score', 'team_stats',
            'created_at', 'updated_at'
        ]

    def get_members(self, obj):
        """Return serialized team members."""
        team_members = TeamMember.objects.filter(team=obj).select_related('character')
        return TeamMemberSerializer(team_members, many=True).data

    def get_member_count(self, obj):
        return obj.members.count()

    def get_team_stats(self, obj):
        """Generate team statistics."""
        members = obj.members.all()
        if not members:
            return {}

        # Species & homewold distribution
        species_count = {}
        homeworld_count = {}

        for member in members:
            species = member.character.species or 'Unknown'
            homeworld = member.character.homeworld or 'Unknown'

            species_count[species] = species_count.get(species, 0) + 1
            homeworld_count[homeworld] = homeworld_count.get(homeworld, 0) + 1

        return {
            'species_distribution': species_count,
            'homeworld_distribution': homeworld_count,
        }

class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding a member to a team"""
    character_id = serializers.IntegerField()

    def validate_character_id(self, value):
        """Validate that the character exists and can be added."""
        try:
            character = Character.objects.get(id=value)
            return value
        except Character.DoesNotExist:
            raise serializers.ValidationError("Character does not exist.")

class RemoveMemberSerializer(serializers.Serializer):
    """Serializer for removing a member from a team"""
    character_id = serializers.IntegerField()

    def validate_character_id(self, value):
        """Validate that the character exists in the team."""
        try:
            character = Character.objects.get(id=value)
            return value
        except Character.DoesNotExist:
            raise serializers.ValidationError("Character does not exist.")

class TeamCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating teams"""


