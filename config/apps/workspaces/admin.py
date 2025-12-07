from django.contrib import admin
from .models import Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'company', 'created_at']
    search_fields = ['name', 'description', 'company__name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'created_by')