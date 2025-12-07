from rest_framework import serializers
from .models import Note, Tag, Vote, NoteHistory
from apps.workspaces.models import Workspace


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'note', 'vote_type', 'created_at']
        read_only_fields = ['user', 'company']


class NoteHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)

    class Meta:
        model = NoteHistory
        fields = ['id', 'title', 'content', 'changed_by', 'changed_by_name', 'changed_at']
        read_only_fields = ['changed_by', 'changed_at']


class NoteListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    company_name = serializers.CharField(source='workspace.company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'note_type', 'is_draft', 'workspace',
            'workspace_name', 'company_name', 'tags', 'created_by',
            'created_by_name', 'created_at', 'updated_at',
            'upvotes', 'downvotes', 'vote_count'
        ]


class NoteDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    company_name = serializers.CharField(source='workspace.company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)
    history = NoteHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'note_type', 'is_draft',
            'workspace', 'workspace_name', 'company_name', 'tags',
            'tag_names', 'created_by', 'created_by_name', 'created_at',
            'updated_at', 'upvotes', 'downvotes', 'vote_count', 'history'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        note = Note.objects.create(**validated_data)

        if tag_names:
            tags = []
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
                tags.append(tag)
            note.tags.set(tags)

        return note

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if tag_names is not None:
            tags = []
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
                tags.append(tag)
            instance.tags.set(tags)

        return instance


class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'note_type', 'is_draft', 'workspace', 'tag_names']
        read_only_fields = ['id']

    # Workspace validation (already present)
    def validate_workspace(self, value):
        user = self.context['request'].user
        if not user.company:
            raise serializers.ValidationError("User must belong to a company")
        if value.company != user.company:
            raise serializers.ValidationError("Workspace does not belong to your company")
        return value

    # --- NEW VALIDATIONS ---
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_note_type(self, value):
        if value not in ['public', 'private']:
            raise serializers.ValidationError("Note type must be 'public' or 'private'")
        return value

    def validate(self, data):
        if not data.get('is_draft', False) and not data.get('content', '').strip():
            raise serializers.ValidationError({"content": "Content cannot be empty for published notes"})
        return data
