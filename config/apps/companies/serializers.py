from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    workspaces_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'created_at',
            'updated_at', 'is_active', 'workspaces_count', 'users_count'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    # ---------------- VALIDATIONS ----------------
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Company name must be at least 3 characters long.")
        if Company.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value

    # ---------------- COUNT METHODS ----------------
    def get_workspaces_count(self, obj):
        return obj.workspaces.filter(is_active=True).count()

    def get_users_count(self, obj):
        return obj.users.filter(is_active=True).count()


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'is_active']

    # ---------------- VALIDATIONS ----------------
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        return value
