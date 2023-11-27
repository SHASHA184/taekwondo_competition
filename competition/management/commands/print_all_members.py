from django.core.management.base import BaseCommand
from competition.views import MemberListView

class Command(BaseCommand):
    help = 'Print all members'

    def handle(self, *args, **kwargs):
        member_list_view = MemberListView()
        
        # Directly call get_queryset, skip the setup
        members = member_list_view.get_queryset()

        for member in members:
            self.stdout.write("----------------------------")
            self.stdout.write(self.style.SUCCESS(f'Member id: {member.id}'))
            self.stdout.write(self.style.SUCCESS(f'Member full name: {member.full_name}'))
            self.stdout.write(self.style.SUCCESS(f'Member weight class: {member.weight_class.name} ({member.weight_class.weight_from} - {member.weight_class.weight_to})'))
            self.stdout.write(self.style.SUCCESS(f'Member belt: {member.belt_rank.name}'))
            self.stdout.write(self.style.SUCCESS(f'Member rating: {member.rating}'))
            self.stdout.write(self.style.SUCCESS(f'Member team: {member.team.name} ({member.team.location})'))
            self.stdout.write("----------------------------")
