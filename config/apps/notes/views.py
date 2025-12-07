from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Note, Tag, Vote, NoteHistory
from .serializers import (
    NoteListSerializer, NoteDetailSerializer, NoteCreateUpdateSerializer,
    TagSerializer, VoteSerializer, NoteHistorySerializer
)
from .permissions import IsOwnerOrReadOnly, CanAccessNote


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Note.objects.select_related(
            'workspace', 'workspace__company', 'created_by', 'updated_by'
        ).prefetch_related('tags', 'votes')

        # Annotate with vote counts
        queryset = queryset.annotate(
            upvotes=Count('votes', filter=Q(votes__vote_type='upvote')),
            downvotes=Count('votes', filter=Q(votes__vote_type='downvote')),
            vote_count=Count('votes', filter=Q(votes__vote_type='upvote')) -
                       Count('votes', filter=Q(votes__vote_type='downvote'))
        )

        # Filter based on view action
        if self.action == 'public_notes':
            return queryset.filter(note_type='public', is_draft=False)

        if self.action == 'my_notes':
            if self.request.user.is_authenticated and self.request.user.company:
                return queryset.filter(workspace__company=self.request.user.company)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action in ['public_notes', 'my_notes']:
            return NoteListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return NoteCreateUpdateSerializer
        return NoteDetailSerializer

    def get_permissions(self):
        if self.action == 'public_notes':
            return [permissions.AllowAny()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        if self.action in ['retrieve', 'list']:
            return [CanAccessNote()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_notes(self, request):
        """List all public published notes"""
        queryset = self.get_queryset()

        # Apply ordering from query params
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering == 'upvotes':
            queryset = queryset.order_by('-upvotes', '-created_at')
        elif ordering == 'downvotes':
            queryset = queryset.order_by('-downvotes', '-created_at')
        elif ordering == 'old':
            queryset = queryset.order_by('created_at')
        elif ordering == 'new':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by(ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_notes(self, request):
        """List notes from user's company workspaces"""
        queryset = self.get_queryset()

        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(title__icontains=search)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a note (upvote or downvote)"""
        note = self.get_object()
        vote_type = request.data.get('vote_type')

        if vote_type not in ['upvote', 'downvote']:
            return Response(
                {'error': 'vote_type must be upvote or downvote'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if note.note_type != 'public' or note.is_draft:
            return Response(
                {'error': 'Can only vote on public published notes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove existing vote if any
        Vote.objects.filter(
            note=note,
            user=request.user if request.user.is_authenticated else None,
            company=request.user.company if request.user.is_authenticated else None
        ).delete()

        # Create new vote
        vote = Vote.objects.create(
            note=note,
            user=request.user if request.user.is_authenticated else None,
            company=request.user.company if request.user.is_authenticated else None,
            vote_type=vote_type
        )

        return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get note history"""
        note = self.get_object()
        history = note.history.all()
        serializer = NoteHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore note from a history entry"""
        note = self.get_object()
        history_id = request.data.get('history_id')

        if not history_id:
            return Response(
                {'error': 'history_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            history_entry = NoteHistory.objects.get(id=history_id, note=note)
        except NoteHistory.DoesNotExist:
            return Response(
                {'error': 'History entry not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create current state as history before restoring
        NoteHistory.objects.create(
            note=note,
            title=note.title,
            content=note.content,
            changed_by=request.user
        )

        # Restore from history
        note.title = history_entry.title
        note.content = history_entry.content
        note.updated_by = request.user
        note.save()

        serializer = self.get_serializer(note)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']