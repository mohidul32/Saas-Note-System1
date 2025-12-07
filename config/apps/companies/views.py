from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Company
from .serializers import CompanySerializer, CompanyListSerializer

# Add MaxLimitPagination here directly
from rest_framework.pagination import PageNumberPagination

class MaxLimitPagination(PageNumberPagination):
    page_size = 10               # default page size
    page_size_query_param = 'limit'
    max_page_size = 50           # maximum allowed


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    pagination_class = MaxLimitPagination  # ← add this
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer

    @action(detail=True, methods=['get'])
    def workspaces(self, request, pk=None):
        """Get all workspaces for this company"""
        company = self.get_object()
        workspaces = company.workspaces.filter(is_active=True)

        from apps.workspaces.serializers import WorkspaceListSerializer
        serializer = WorkspaceListSerializer(workspaces, many=True)
        return Response(serializer.data)
