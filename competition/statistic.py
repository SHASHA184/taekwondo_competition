from django.db.models import Count
from .models import Competition, Member, Match, Team, MatchMember, GENDER_CHOICES
from django.shortcuts import render
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth, TruncYear, DenseRank
from django.db.models import Max, OuterRef, Subquery, F, Window


def competition_stats(request):
    finished_competitions = Competition.objects.filter(finished=True)
    winners_list = []

    for competition in finished_competitions:
        competition_categories = competition.competitioncategory_set.all()

        for category in competition_categories:
            # Assuming semifinal is round 4 and final is round 5
            final_round_number = 5
            semifinal_round_number = 4

            # Get the top two performers in the final round
            final_round = Match.objects.filter(
                competition_category=category, round=final_round_number)
            if not final_round:
                continue
            first_place = MatchMember.objects.filter(
                match__in=final_round, status=1).order_by('-score')[:1]
            second_place = MatchMember.objects.filter(
                match__in=final_round, status=2).order_by('-score')[:1]
            # Identify the participants who lost in the semifinal round
            semifinal_losers = MatchMember.objects.filter(
                match__competition_category=category,
                match__round=semifinal_round_number,
                status=2  # Assuming status '2' means 'Lose'
            )

            # Find the winner of the third-place match between the semifinal losers
            third_place = MatchMember.objects.filter(
                match__competition_category=category,
                match__round=semifinal_round_number,
                member__in=[loser.member for loser in semifinal_losers],
                status=1  # Winner of the third-place match
            ).first()

            # print first place and second place
            if first_place:
                print(f'First place: {first_place[0].member.full_name}')
                print(f'Second place: {second_place[0].member.full_name}')
                print(f'Third place: {third_place.member.full_name}')

            winners = {
                'category': category.weight_class,
                'first_place': first_place[0].member.full_name if first_place else "N/A",
                'second_place': second_place[0].member.full_name if second_place else "N/A",
                'third_place': third_place.member.full_name if third_place else "N/A",
            }
            winners_list.append(winners)
        print("Debug: Winners List")
        print(winners_list)

    ongoing_competitions = Competition.objects.filter(finished=False)

    competitions = Competition.objects.all()

    # Count competitions by month
    competitions_by_month = Competition.objects.annotate(
        month=TruncMonth('date')).values('month').annotate(count=Count('id'))

    # Count competitions by year
    competitions_by_year = Competition.objects.annotate(
        year=TruncYear('date')).values('year').annotate(count=Count('id'))

    competitions_by_location = Competition.objects.values(
        'location').annotate(count=Count('id')).order_by('-count')

    context = {
        'finished_competitions': finished_competitions,
        'ongoing_competitions': ongoing_competitions,
        'competitions': competitions,
        'competitions_by_month': competitions_by_month,
        'competitions_by_year': competitions_by_year,
        'competitions_by_location': competitions_by_location,
        'winners_list': winners_list,
    }
    # In your view, right before rendering the template:

    return render(request, 'statistics/competition_stats.html', context)


def member_stats(request):
    # Retrieve all members from the database
    members = Member.objects.select_related('belt_rank', 'weight_class', 'team').all()

    # Calculate the total number of members
    total_members = members.count()

    # Calculate the average age of members
    average_age = members.aggregate(avg_age=Avg('age'))['avg_age']

    # Create a mapping of gender choices for display
    gender_display_map = dict(GENDER_CHOICES)

    # Annotate members with gender count
    gender_distribution_raw = members.values('gender').annotate(count=Count('gender'))

    # Convert gender_distribution to include display labels
    gender_distribution = [
        {'gender': gender_display_map.get(gender['gender'], 'N/A'), 'count': gender['count']}
        for gender in gender_distribution_raw
    ]

    # Calculate the distribution of members by belt rank
    belt_rank_distribution = members.values('belt_rank__name').annotate(count=Count('belt_rank')).order_by('-count')

    # Calculate the distribution of members by weight class
    weight_class_distribution = members.values('weight_class__name').annotate(count=Count('weight_class')).order_by('-count')

    # Calculate the distribution of members by team
    team_distribution = members.values('team__name').annotate(count=Count('team')).order_by('-count')

    context = {
        'members': members,
        'total_members': total_members,
        'average_age': average_age,
        'gender_distribution': gender_distribution,
        'belt_rank_distribution': belt_rank_distribution,
        'weight_class_distribution': weight_class_distribution,
        'team_distribution': team_distribution,
    }
    return render(request, 'statistics/member_stats.html', context)


def match_stats(request):
    total_matches = Match.objects.count()
    finished_matches = Match.objects.filter(finished=True).count()
    ongoing_matches = Match.objects.filter(finished=False).count()
    matches = Match.objects.select_related(
        'competition_category', 'judge').prefetch_related('matchmember_set')

    context = {
        'total_matches': total_matches,
        'finished_matches': finished_matches,
        'ongoing_matches': ongoing_matches,
        'matches': matches,
    }
    return render(request, 'statistics/match_stats.html', context)


def team_stats(request):
    # Calculate team statistics
    teams = Team.objects.annotate(
        num_members=Count('member'),
        avg_age=Avg('member__age'),
        total_rating=Sum('member__rating')
    )

    context = {
        'teams': teams,
    }
    return render(request, 'statistics/team_stats.html', context)
