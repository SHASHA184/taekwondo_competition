from django.core.management.base import BaseCommand
import random
from competition.models import Competition, CompetitionCategory, Match, Member, MatchMember, Judge, ROUND_CHOICES, BASE_RATING
from django.utils import timezone
from datetime import timedelta
from itertools import combinations
from math import ceil, log2


class Command(BaseCommand):
    help = 'Simulate matches'

    def handle(self, *args, **kwargs):
        simulate_matches()


def calculate_elo_rating(rating_a, rating_b, score_a, score_b, k_factor=32):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

    new_rating_a = max(rating_a + k_factor *
                       (score_a - expected_a), BASE_RATING)
    new_rating_b = max(rating_b + k_factor *
                       (score_b - expected_b), BASE_RATING)

    return new_rating_a, new_rating_b


def simulate_match_outcome(member_a, member_b):
    """
    Simulate a match outcome based on members' ratings.
    """
    prob_a_wins = 1 / (1 + 10 ** ((member_b.rating - member_a.rating) / 400))
    if random.random() < prob_a_wins:
        return 1, 0  # Member A wins
    else:
        return 0, 1  # Member B wins


def simulate_matches(competitions=None):
    if competitions is None:
        competitions = Competition.objects.all()
    else:
        competitions = Competition.objects.filter(pk__in=competitions)
    categories = CompetitionCategory.objects.filter(
        competition__in=competitions)

    if not Judge.objects.exists():
        print("No judges available.")
        return

    matches = []
    successful_competitions = []

    for competition in competitions:
        for category in categories:
            all_members = list(Member.objects.filter(
                weight_class=category.weight_class))
            all_matches = []
            random.shuffle(all_members)

            if len(all_members) < 2:
                continue

            # extra round
            if len(all_members) % 2 != 0:
                # Add a "bye" member
                extra_match, score_a, score_b = create_match(
                    category, Judge.objects.all(), all_members.pop(), all_members.pop(), 1)
                all_members.append(extra_match.matchmember_set.get(
                    status=1).member)
                all_matches.append(extra_match)

            # 1/16
            if len(all_members) > 16:
                matches, all_members = create_round(
                    category, Judge.objects.all(), all_members, 1, 16)
                all_matches.extend(matches)

            # 1/8
            if len(all_members) > 8:
                matches, all_members = create_round(
                    category, Judge.objects.all(), all_members, 2, 8)
                all_matches.extend(matches)

            # 1/4
            if len(all_members) > 4:
                matches, all_members = create_round(
                    category, Judge.objects.all(), all_members, 3, 4)
                all_matches.extend(matches)

            # 1/2
            semifinal_losers = []
            if len(all_members) > 2:
                matches, all_members = create_round(
                    category, Judge.objects.all(), all_members, 4, 2)
                all_matches.extend(matches)
                # Collect the losers for the third-place match
                for match in matches:
                    semifinal_losers.append(
                        match.matchmember_set.get(status=2).member)

            # Third-place match
            if len(semifinal_losers) == 2:
                third_place_match, score_a, score_b = create_match(
                    category, Judge.objects.all(), semifinal_losers[0], semifinal_losers[1], 4)  # Assume round 6 is for third-place
                all_matches.append(third_place_match)

            # Final
            if len(all_members) > 1:
                matches, all_members = create_round(
                    category, Judge.objects.all(), all_members, 5, 1)
                all_matches.extend(matches)

            for member in all_members:
                member.save()

        successful_competitions.append(competition.pk)

    return successful_competitions


def create_round(category, judges, members, round_number, count_after):
    matches = []
    while len(members) > count_after:
        for member1, member2 in combinations(members, 2):
            match, score_a, score_b = create_match(
                category, judges, member1, member2, round_number)
            matches.append(match)
            members.remove(member1)
            members.remove(member2)
            members.append(match.matchmember_set.get(status=1).member)
            break
    return matches, members


def create_match(category, judges, member1, member2, round_number):
    # Simulate match outcome and calculate new Elo ratings
    score_a, score_b = simulate_match_outcome(member1, member2)
    new_rating_a, new_rating_b = calculate_elo_rating(
        member1.rating, member2.rating, score_a, score_b)

    # Update member ratings
    member1.rating, member2.rating = new_rating_a, new_rating_b

    # Create the match
    match = Match.objects.create(
        match_time=timezone.now() + timedelta(days=round_number),
        competition_category=category,
        judge=random.choice(judges),
        round=round_number,
        finished=True
    )

    # Create MatchMember instances
    MatchMember.objects.create(
        match=match, member=member1, score=score_a, status=1 if score_a > score_b else 2)
    MatchMember.objects.create(
        match=match, member=member2, score=score_b, status=1 if score_b > score_a else 2)

    print(
        f"Match created in round {round_number}: {member1.full_name} vs {member2.full_name} ({score_a}:{score_b})")

    # Return the match and scores
    return match, score_a, score_b
