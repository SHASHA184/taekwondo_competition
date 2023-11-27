from competition.models import Match
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Drop all matches'

    def handle(self, *args, **kwargs):
        Match.objects.all().delete()
        print('All matches dropped.')
