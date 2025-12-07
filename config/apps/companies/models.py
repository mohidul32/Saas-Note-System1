from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    """
    Company model - Multi-tenant root entity
    Each company has multiple workspaces and users
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Company.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def total_workspaces(self):
        """Get count of active workspaces"""
        return self.workspaces.filter(is_active=True).count()

    @property
    def total_users(self):
        """Get count of active users"""
        return self.users.filter(is_active=True).count()

    @property
    def total_notes(self):
        """Get count of all notes across all workspaces"""
        from apps.notes.models import Note
        workspace_ids = self.workspaces.values_list('id', flat=True)
        return Note.objects.filter(workspace_id__in=workspace_ids).count()