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

    def get_workspaces_count(self, obj):
        return obj.workspaces.filter(is_active=True).count()

    def get_users_count(self, obj):
        return obj.users.filter(is_active=True).count()


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'is_active']