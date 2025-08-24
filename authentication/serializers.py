from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirmation',
            'first_name', 'last_name'
        ]

    def validate(self, data):
        """Ensure password and confirmation match."""
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Password and confirmation do not match.")
        return data

    def create(self, validated_data):
        """Create a new user with the validated data."""
        validated_data.pop('password_confirmation')
        user = User.objects.create_user(**validated_data)
        return user
