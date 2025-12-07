from django.db import models
from django.utils.text import slugify


class Workspace(models.Model):
    """Container for notes within a company"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='workspaces')
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_workspaces')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspaces'
        ordering = ['-created_at']
        unique_together = [['company', 'slug']]
        indexes = [
            models.Index(fields=['company', 'slug']),
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)