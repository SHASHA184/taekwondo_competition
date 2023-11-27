from django.core.management.base import BaseCommand
from competition.views import CompetitionListView

class Command(BaseCommand):
    help = 'Print all competitions'

    def handle(self, *args, **kwargs):
        competition_list_view = CompetitionListView()

        # Directly call get_queryset, skip the setup
        competitions = competition_list_view.get_queryset()

        for competition in competitions:
            self.stdout.write("----------------------------")
            self.stdout.write(self.style.SUCCESS(f'Competition id: {competition.id}'))
            self.stdout.write(self.style.SUCCESS(f'Competition name: {competition.name}'))
            self.stdout.write(self.style.SUCCESS(f'Competition location: {competition.location}'))
            self.stdout.write(self.style.SUCCESS(f'Competition date: {competition.date}'))
            self.stdout.write(self.style.SUCCESS(f'Competition finished: {competition.finished}'))
            self.stdout.write(self.style.SUCCESS(f'Competition first_place: {competition.first_place}'))
            self.stdout.write(self.style.SUCCESS(f'Competition second_place: {competition.second_place}'))
            self.stdout.write(self.style.SUCCESS(f'Competition third_place: {competition.third_place}'))
            self.stdout.write("----------------------------")
