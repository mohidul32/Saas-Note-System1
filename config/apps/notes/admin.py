from django.contrib import admin
from .models import Note, Tag, Vote, NoteHistory


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'workspace', 'note_type', 'is_draft', 'created_by', 'created_at']
    list_filter = ['note_type', 'is_draft', 'created_at']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['note', 'company', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']


@admin.register(NoteHistory)
class NoteHistoryAdmin(admin.ModelAdmin):
    list_display = ['note', 'changed_by', 'changed_at']
    list_filter = ['changed_at']
    readonly_fields = ['changed_at']