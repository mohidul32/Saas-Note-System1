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

    # ---------------- VALIDATIONS ----------------
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Workspace name cannot be empty")
        if len(value) < 3:
            raise serializers.ValidationError("Workspace name must be at least 3 characters long")
        # Prevent duplicate name within same company
        user = self.context['request'].user
        if user and user.company and Workspace.objects.filter(name__iexact=value, company=user.company).exists():
            raise serializers.ValidationError("A workspace with this name already exists in your company")
        return value

    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value

    def validate_company(self, value):
        user = self.context['request'].user
        if not user.company:
            raise serializers.ValidationError("You must belong to a company to create a workspace")
        if value != user.company:
            raise serializers.ValidationError("You can only create a workspace for your own company")
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

    # ---------------- VALIDATIONS ----------------
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Workspace name cannot be empty")
        return value
