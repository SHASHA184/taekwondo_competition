from typing import Any
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import *
from .forms import *
from django.db.models import Count, Max
from django.utils import timezone
from competition.management.commands.simulate_matches import simulate_matches
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.views import LogoutView
from functools import wraps


def generate_matches(request):
    if request.method == 'POST':
        # Handle form submission and match generation here
        selected_competitions = request.POST.getlist('competitions')

        # Call your `simulate_matches` function with the selected competitions
        successful_competitions = simulate_matches(selected_competitions)

        Competition.objects.filter(id__in=successful_competitions).update(
            finished=True)
        return redirect('matches-list')
    else:
        # Filter competitions based on date range only for initial page load
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        competitions = Competition.objects.filter(finished=False)

        if date_from:
            print("Date from:", date_from)
            competitions = competitions.filter(date__gte=date_from)

        if date_to:
            competitions = competitions.filter(date__lte=date_to)

        return render(request, 'competition/competition_simulate_matches.html', {'competitions': competitions, 'date_from': date_from, 'date_to': date_to})


def home(request):
    return render(request, 'home.html')


def competition_list(request):
    # Get competitions
    competitions = Competition.objects.all()

    # Filtering
    location_filter = request.GET.getlist('location')  # Change to getlist
    if location_filter:
        # Use __in for multiple locations
        competitions = competitions.filter(location__in=location_filter)

    date_from_filter = request.GET.get('date_from')
    date_to_filter = request.GET.get('date_to')
    if date_from_filter and date_to_filter:
        competitions = competitions.filter(
            date__range=[date_from_filter, date_to_filter])
    elif date_from_filter:
        competitions = competitions.filter(date__gte=date_from_filter)
    elif date_to_filter:
        competitions = competitions.filter(date__lte=date_to_filter)

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by in ['name', 'date', 'location']:
        competitions = competitions.order_by(sort_by)

    locations = Competition.objects.values_list(
        'location', flat=True).distinct()
    return render(request, 'competition/competition_list.html', {
        'competitions': competitions,
        'locations': locations,
        'selected_locations': location_filter
    })


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'competition/competition_detail.html'
    context_object_name = 'competition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add competition categories to the context
        context['categories'] = self.object.competitioncategory_set.select_related(
            'weight_class').all()
        return context


class CompetitionCreateView(CreateView):
    model = Competition
    form_class = CompetitionForm
    template_name = 'competition/competition_create.html'
    success_url = reverse_lazy('competitions-list')


def competition_edit(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            return redirect('competitions-list')
    else:
        form = CompetitionForm(instance=competition)
    return render(request, 'competition/competition_edit.html', {'form': form})


def competition_delete(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    competition.delete()
    return redirect('competitions-list')


class WeightClassListView(ListView):
    model = WeightClass
    template_name = 'weight_class/weight_classes_list.html'
    context_object_name = 'weight_classes'

    def get_queryset(self):
        # Filter weight classes based on your criteria
        return WeightClass.objects.all()  # You can adjust this queryset as needed


class WeightClassCreateView(CreateView):
    model = WeightClass
    form_class = WeightClassForm
    template_name = 'weight_class/weight_class_create.html'
    success_url = reverse_lazy('weight_classes_list')


class WeightClassDetailView(DetailView):
    model = WeightClass
    template_name = 'weight_class/weight_class_detail.html'
    context_object_name = 'weight_class'


def weight_class_edit(request, pk):
    weight_class = get_object_or_404(WeightClass, pk=pk)
    if request.method == 'POST':
        form = WeightClassForm(request.POST, instance=weight_class)
        if form.is_valid():
            form.save()
            return redirect('weight_class_detail', pk=weight_class.pk)
    else:
        form = WeightClassForm(instance=weight_class)
    return render(request, 'weight_class/weight_class_edit.html', {'form': form})


def weight_class_delete(request, weight_class_id):
    weight_class = get_object_or_404(WeightClass, pk=weight_class_id)
    weight_class.delete()
    return redirect('weight_classes_list')


def member_list(request):
    members = Member.objects.all()
    # search by full name
    full_name_filter = request.GET.get('full_name')
    if full_name_filter:
        members = members.filter(full_name__icontains=full_name_filter)

    # Filtering
    team_filter = request.GET.getlist('team')  # Get a list of selected teams
    if team_filter:
        members = members.filter(team__name__in=team_filter)

    rating_filter_from = request.GET.get('rating_from')
    rating_filter_to = request.GET.get('rating_to')
    if rating_filter_from and rating_filter_to:
        members = members.filter(
            rating__range=[rating_filter_from, rating_filter_to])
    elif rating_filter_from:
        members = members.filter(rating__gte=rating_filter_from)
    elif rating_filter_to:
        members = members.filter(rating__lte=rating_filter_to)

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by in ['full_name', 'age', 'gender', 'belt_rank', 'weight_class', 'rating', 'team']:
        members = members.order_by(sort_by)

    # Get all teams for the select multiple filter
    teams = Team.objects.all()

    return render(request, 'member/members_list.html', {'members': members, 'teams': teams})


class MemberDetailView(DetailView):
    model = Member
    template_name = 'member/member_detail.html'
    context_object_name = 'member'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the member's team to the context
        context['team'] = self.object.team
        return context


def member_create(request):
    age = request.GET.get('age')
    gender = request.GET.get('gender')

    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('members-list')
        else:
            print("Invalid form:", form.errors)
    else:
        form = MemberForm()
        if age and gender:
            form.fields['weight_class'].queryset = WeightClass.objects.filter(
                years_from__lte=age, years_to__gte=age, gender=gender)

    return render(request, 'member/member_create.html', {'form': form, 'age': age, 'gender': gender})


def member_delete(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.delete()
    return redirect('members-list')


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members-list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'member/member_edit.html', {'form': form})


def match_list(request):
    # Filter matches based on your criteria
    matches = Match.objects.annotate(member_count=Count(
        'matchmember')).filter(member_count__gt=0)
    match_members = MatchMember.objects.filter(match__in=matches)

    competition_filter = request.GET.get('competition')
    if competition_filter:
        # find competition by name
        matches = matches.filter(
            competition_category__competition__name__icontains=competition_filter)

    # Apply filters
    date_from_filter = request.GET.get('date_from')
    date_to_filter = request.GET.get('date_to')
    if date_from_filter and date_to_filter:
        matches = matches.filter(
            match_time__range=[date_from_filter, date_to_filter])
    elif date_from_filter:
        matches = matches.filter(match_time__gte=date_from_filter)
    elif date_to_filter:
        matches = matches.filter(match_time__lte=date_to_filter)

    finished_filter = request.GET.get('finished')
    if finished_filter:
        matches = matches.filter(finished=finished_filter)

    round_filter = request.GET.get('round')
    if round_filter and round_filter != 'all':
        matches = matches.filter(round=round_filter)

    # Apply sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'date':
        matches = matches.order_by('date')
    elif sort_by == 'members':
        matches = matches.annotate(member_count=Count(
            'matchmember')).order_by('-member_count')
    elif sort_by == 'round':
        matches = matches.order_by('round')

    queryset = []
    for match in matches:
        members = match_members.filter(match=match)
        if len(members) == 2:
            queryset.append(
                {"match": match, "member1": members[0], "member2": members[1]})

    result = {'matches': queryset}

    return render(request, 'match/matches_list.html', result)


def match_create(request):
    competitions = Competition.objects.all()
    competition_categories = CompetitionCategory.objects.all()
    competition_filter = request.GET.get('competition')
    competition_category_filter = request.GET.get('competition_category')

    if request.method == 'POST':
        post_data = request.POST.copy()
        competition_category = CompetitionCategory.objects.get(
            id=competition_category_filter)
        post_data['competition_category'] = competition_category_filter
        form = MatchForm(post_data)

        if form.is_valid():
            with transaction.atomic():
                match = form.save()
                match.competition_category = competition_category
                formset = MatchMemberFormSet(request.POST, instance=match)
                if formset.is_valid():
                    formset.instance = match
                    formset.save()
                return redirect('matches-list')
    else:
        form = MatchForm()
        formset = MatchMemberFormSet(queryset=MatchMember.objects.none())

        if competition_filter:
            competition_categories = CompetitionCategory.objects.filter(
                competition_id=competition_filter
            )

        if competition_category_filter:
            competition_category = CompetitionCategory.objects.get(
                id=competition_category_filter)
            weight_class_id = competition_category.weight_class.id
            members_queryset = Member.objects.filter(
                weight_class_id=weight_class_id)

            for match_member_form in formset:
                match_member_form.fields['member'].queryset = members_queryset

    return render(request, 'match/match_create.html', {
        'form': form,
        'formset': formset,
        'competitions': competitions,
        'competition_categories': competition_categories,
        'competition_filter': competition_filter,
        'competition_category_filter': competition_category_filter
    })


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    members = MatchMember.objects.filter(match=match)
    winner = None
    if members:
        highest_score = max(members, key=lambda m: m.score)
        winner = highest_score.member if highest_score.score > 0 else None
    return render(request, 'match/match_detail.html', {'match': match, 'members': members, 'winner': winner})


def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)
    match_member_instances = MatchMember.objects.filter(match=match)

    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        formset = MatchMemberFormSet(request.POST, instance=match)

        try:
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    match = form.save()
                    formset.instance = match
                    formset.save()

                    # Logic to determine the winner and finish the match
                    match_members = match.matchmember_set.all()
                    highest_score = match_members.aggregate(Max('score'))[
                        'score__max']

                    if highest_score > 0:  # Check if the highest score is greater than 0
                        winner = match_members.filter(
                            score=highest_score).first()
                        match.winner = winner.member if winner else None
                        match.finished = True  # Mark the match as finished if there's a winner
                    else:
                        match.finished = False  # Do not mark as finished if highest score is 0

                    match.save()

                    return redirect('matches-list')

            else:
                print("Invalid formset:", formset.errors)
                print("Invalid form:", form.errors)

        except ValidationError as e:
            print("Validation error:", e)
            form.add_error(None, e)

    else:
        # Initialize the form and formset for GET request
        form = MatchForm(instance=match)
        formset = MatchMemberFormSet(
            instance=match, queryset=match_member_instances)

    return render(request, 'match/match_edit.html', {
        'form': form,
        'formset': formset,
    })


def match_delete(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    match.delete()
    return redirect('matches-list')


class JudgeListView(ListView):
    model = Judge
    template_name = 'judge/judges_list.html'
    context_object_name = 'judges'

    def get_queryset(self):
        # Filter judges based on your criteria
        return Judge.objects.all()  # You can adjust this queryset as needed


class JudgeCreateView(CreateView):
    model = Judge
    form_class = JudgeForm
    template_name = 'judge/judge_create.html'
    success_url = reverse_lazy('judges-list')


class JudgeDetailView(DetailView):
    model = Judge
    template_name = 'judge/judge_detail.html'
    context_object_name = 'judge'


def judge_edit(request, pk):
    judge = get_object_or_404(Judge, pk=pk)
    if request.method == 'POST':
        form = JudgeForm(request.POST, instance=judge)
        if form.is_valid():
            form.save()
            return redirect('judges-list')
    else:
        form = JudgeForm(instance=judge)
    return render(request, 'judge/judge_edit.html', {'form': form})


def judge_delete(request, judge_id):
    judge = get_object_or_404(Judge, pk=judge_id)
    judge.delete()
    return redirect('judges-list')


class JudgeQualificationListView(ListView):
    model = JudgeQualification
    template_name = 'judge/judge_qualifications_list.html'
    context_object_name = 'qualifications'

    def get_queryset(self):
        # Filter qualifications based on your criteria
        # You can adjust this queryset as needed
        return JudgeQualification.objects.all()


class JudgeQualificationCreateView(CreateView):
    model = JudgeQualification
    form_class = JudgeQualificationForm
    template_name = 'judge/judge_qualification_create.html'
    success_url = reverse_lazy('qualification-list')


def judge_qualification_edit(request, pk):
    qualification = get_object_or_404(JudgeQualification, pk=pk)
    if request.method == 'POST':
        form = JudgeQualificationForm(request.POST, instance=qualification)
        if form.is_valid():
            form.save()
            return redirect('qualification-list')
    else:
        form = JudgeQualificationForm(instance=qualification)
    return render(request, 'judge/judge_qualification_edit.html', {'form': form})


def judge_qualification_delete(request, qualification_id):
    qualification = get_object_or_404(JudgeQualification, pk=qualification_id)
    qualification.delete()
    return redirect('qualification-list')


def team_list(request):
    teams = Team.objects.annotate(member_count=Count('member'))

    # Filtering
    coach_filter = request.GET.get('coach')
    if coach_filter:
        teams = teams.filter(coach__full_name__icontains=coach_filter)

    location_filter = request.GET.getlist('location')  # Change to getlist
    if location_filter:
        # Use __in for multiple locations
        teams = teams.filter(location__in=location_filter)

    member_count_filter_from = request.GET.get('member_count_from')
    member_count_filter_to = request.GET.get('member_count_to')
    if member_count_filter_from and member_count_filter_to:
        teams = teams.filter(
            member_count__range=[member_count_filter_from, member_count_filter_to])
    elif member_count_filter_from:
        teams = teams.filter(member_count__gte=member_count_filter_from)
    elif member_count_filter_to:
        teams = teams.filter(member_count__lte=member_count_filter_to)

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by in ['name', 'coach', 'member_count']:
        teams = teams.order_by(sort_by)

    locations = Team.objects.values_list(
        'location', flat=True).distinct()

    context = {'teams': teams, 'locations': locations, }

    return render(request, 'team/teams_list.html', context)


class TeamCreateView(CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'team/team_create.html'
    success_url = reverse_lazy('teams-list')


class TeamDetailView(DetailView):
    model = Team
    template_name = 'team/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        # Add the coaches to the context
        context['coaches'] = Coach.objects.filter(team=self.object)
        context['members'] = Member.objects.filter(team=self.object)
        return context


def edit_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    team_form = TeamForm(instance=team)
    member_formset = MemberFormSet(instance=team)
    coach_formset = CoachFormSet(instance=team)

    if request.method == 'POST':
        team_form = TeamForm(request.POST, instance=team)
        member_formset = MemberFormSet(request.POST, instance=team)
        coach_formset = CoachFormSet(request.POST, instance=team)

        if team_form.is_valid() and member_formset.is_valid() and coach_formset.is_valid():
            team_form.save()
            member_formset.save()
            coach_formset.save()
            return redirect('team-detail', pk=team.pk)

    return render(request, 'team/team_edit.html', {
        'team_form': team_form,
        'member_formset': member_formset,
        'coach_formset': coach_formset
    })


def team_delete(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    team.delete()
    return redirect('teams-list')


class CoachListView(ListView):
    model = Coach
    template_name = 'coach/coach_list.html'
    context_object_name = 'coaches'

    def get_queryset(self):
        # Filter coaches based on your criteria
        return Coach.objects.all()  # You can adjust this queryset as needed


class CoachCreateView(CreateView):
    model = Coach
    form_class = CoachForm
    template_name = 'coach/coach_create.html'
    success_url = reverse_lazy('coaches-list')


class CoachDetailView(DetailView):
    model = Coach
    template_name = 'coach/coach_detail.html'
    context_object_name = 'coach'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the coach's team to the context
        context['team'] = self.object.team
        return context


def coach_edit(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    if request.method == 'POST':
        form = CoachForm(request.POST, instance=coach)
        if form.is_valid():
            form.save()
            return redirect('coaches-list')
    else:
        form = CoachForm(instance=coach)
    return render(request, 'coach/coach_edit.html', {'form': form})


def coach_delete(request, coach_id):
    coach = get_object_or_404(Coach, pk=coach_id)
    coach.delete()
    return redirect('coaches-list')


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        group_name = 'Admin'
        # Try to get the group; create it if it doesn't exist
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return super(UserRegistrationView, self).form_valid(form)
