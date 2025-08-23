from rest_framework import serializers

from .models import Character, Master


class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ['master_name']

class CharacterListSerializer(serializers.ModelSerializer):
    """Serializer for character list (minimal data)"""
    class Meta:
        model = Character
        fields = [
            'id', 'name', 'image_url', 'species',
            'homeworld', 'is_evil', 'evilness_score'
        ]

class CharacterDetailSerializer(serializers.ModelSerializer):
    """Serializer for character detail view (full data)"""
    affiliations = serializers.ListField(read_only=True)
    masters = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'height', 'mass', 'gender', 'homeworld',
            'species', 'image_url', 'affiliations', 'masters',
            'biography', 'is_evil', 'evilness_score', 'evilness_explanation',
            'created_at', 'updated_at'
        ]

    def get_masters(self, obj):
        """Resturn a list of masters for the character."""
        masters = Master.objects.filter(character=obj)
        return [master.master_name for master in masters]
