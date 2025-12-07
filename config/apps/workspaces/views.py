from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workspace
from .serializers import WorkspaceSerializer, WorkspaceListSerializer


class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.select_related('company', 'created_by').all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.company:
            return Workspace.objects.none()
        return Workspace.objects.filter(company=user.company).select_related(
            'company', 'created_by'
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkspaceListSerializer
        return WorkspaceSerializer

    def perform_create(self, serializer):
        serializer.save(
            company=self.request.user.company,
            created_by=self.request.user
        )

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Get all notes in this workspace"""
        workspace = self.get_object()
        notes = workspace.notes.filter(is_draft=False).select_related(
            'created_by', 'updated_by'
        ).prefetch_related('tags')

        from apps.notes.serializers import NoteListSerializer
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)