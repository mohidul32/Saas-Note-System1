from rest_framework import serializers
from .models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'description', 'company', 'company_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'is_active', 'notes_count'
        ]
        read_only_fields = ['slug', 'created_by', 'created_at', 'updated_at']

    def get_notes_count(self, obj):
        return obj.notes.count()

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Workspace name cannot be empty")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['company'] = user.company
        validated_data['created_by'] = user
        return super().create(validated_data)


class WorkspaceListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'company_name', 'created_at',
            'is_active', 'notes_count'
        ]

    def get_notes_count(self, obj):
        return obj.notes.filter(is_draft=False).count()