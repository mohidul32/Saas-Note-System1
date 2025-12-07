from django.core.management.base import BaseCommand
from apps.notes.models import NoteHistory


class Command(BaseCommand):
    help = 'Clean up note history older than 7 days'

    def handle(self, *args, **options):
        self.stdout.write('Starting history cleanup...')

        deleted_count = NoteHistory.cleanup_old_history()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old history entries')
        )