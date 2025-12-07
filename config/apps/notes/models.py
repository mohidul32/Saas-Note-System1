from django.db import models
from django.utils import timezone
from datetime import timedelta


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Note(models.Model):
    NOTE_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    title = models.CharField(max_length=500, db_index=True)
    content = models.TextField()
    note_type = models.CharField(max_length=10, choices=NOTE_TYPE_CHOICES, default='private', db_index=True)
    is_draft = models.BooleanField(default=False, db_index=True)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='updated_notes')

    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'note_type', 'is_draft']),
            models.Index(fields=['note_type', 'is_draft', 'created_at']),
            models.Index(fields=['title']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def vote_count(self):
        upvotes = self.votes.filter(vote_type='upvote').count()
        downvotes = self.votes.filter(vote_type='downvote').count()
        return upvotes - downvotes

    @property
    def upvotes(self):
        return self.votes.filter(vote_type='upvote').count()

    @property
    def downvotes(self):
        return self.votes.filter(vote_type='downvote').count()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_note = None if is_new else Note.objects.filter(pk=self.pk).first()

        super().save(*args, **kwargs)

        # Create history entry on update
        if not is_new and old_note and (old_note.content != self.content or old_note.title != self.title):
            NoteHistory.objects.create(
                note=self,
                title=old_note.title,
                content=old_note.content,
                changed_by=self.updated_by
            )


class Vote(models.Model):
    VOTE_TYPE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='votes', null=True,
                                blank=True)
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        unique_together = [['note', 'user'], ['note', 'company']]
        indexes = [
            models.Index(fields=['note', 'vote_type']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.vote_type} on {self.note.title}"


class NoteHistory(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='history')
    title = models.CharField(max_length=500)
    content = models.TextField()
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='history_changes')
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'note_history'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['note', '-changed_at']),
            models.Index(fields=['changed_at']),
        ]

    def __str__(self):
        return f"History of {self.note.title} at {self.changed_at}"

    @classmethod
    def cleanup_old_history(cls):
        """Delete history entries older than configured retention days"""
        from django.conf import settings
        cutoff_date = timezone.now() - timedelta(days=settings.HISTORY_RETENTION_DAYS)
        deleted_count = cls.objects.filter(changed_at__lt=cutoff_date).delete()[0]
        return deleted_count