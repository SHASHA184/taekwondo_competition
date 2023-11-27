from django.core.management.base import BaseCommand
from competition.views import MatchListView

class Command(BaseCommand):
    help = 'Print all matches'

    def handle(self, *args, **kwargs):
        match_list_view = MatchListView()
        
        # Directly call get_queryset, skip the setup
        matches = match_list_view.get_queryset()

        for match in matches:
            self.stdout.write("----------------------------")
            self.stdout.write(self.style.SUCCESS(f'Match id: {match.id}'))
            self.stdout.write(self.style.SUCCESS(f'Match time: {match.match_time}'))
            self.stdout.write(self.style.SUCCESS(f'Match finished: {match.finished}'))
            self.stdout.write(self.style.SUCCESS(f'Match competition: {match.competition.name}'))
            self.stdout.write(self.style.SUCCESS(f'Match judge: {match.judge.full_name}'))
            self.stdout.write("----------------------------")