from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Team, TeamMember
from .serializers import (
    TeamListSerializer,
    TeamDetailSerializer,
    TeamCreateUpdateSerializer,
    AddMemberSerializer,
    RemoveMemberSerializer,
)
from characters.models import Character


class TeamListCreateView(generics.ListCreateAPIView):
    """
    List all teams or create a new team

    GET /api/teams/ - List all teams
    POST /api/teams/ - Create a new team
    """

    queryset = Team.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamCreateUpdateSerializer
        return TeamListSerializer

    def perform_create(self, serializer):
        # Set owner if user is authenticated
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific team

    GET /api/teams/{id}/ - Get team details
    PUT /api/teams/{id}/ - Update team
    DELETE /api/teams/{id}/ - Delete team
    """

    queryset = Team.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return TeamCreateUpdateSerializer
        return TeamDetailSerializer


@api_view(["POST"])
def add_member(request, team_id):
    """
    Add a character to a team

    POST /api/teams/{team_id}/add-member/
    {
        "character_id": 1
    }
    """
    team = get_object_or_404(Team, id=team_id)
    serializer = AddMemberSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    character_id = serializer.validated_data["character_id"]

    try:
        character = Character.objects.get(id=character_id)

        # Check if character can be added
        can_add, message = team.can_add_member(character)
        if not can_add:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        # Add member to team
        team_member = TeamMember.objects.create(team=team, character=character)

        # Return serialized team member
        team_serailizer = TeamDetailSerializer(team)
        return Response({
            "message": f"{character.name} added to team successfully.",
            "team": team_serailizer.data,
        }, status=status.HTTP_201_CREATED)

    except Character.DoesNotExist:
        return Response(
            {"error": "Character not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def remove_member(request, team_id):
    """
    Remove a character from a team

    POST /api/teams/{team_id}/remove-member/
    {
        "character_id": 1
    }
    """
    team = get_object_or_404(Team, id=team_id)
    serializer = RemoveMemberSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    character_id = serializer.validated_data["character_id"]

    try:
        character = Character.objects.get(id=character_id)

        # Try to remove member
        if team.remove_member(character):
            team_serializer = TeamDetailSerializer(team)
            return Response({
                "message": f"{character.name} removed from team successfully.",
                "team": team_serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": f"{character.name} is not a member of this team."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Character.DoesNotExist:
        return Response(
            {"error": "Character not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
