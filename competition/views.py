from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Competition, Team, Coach, Member, Belt, WeightClass, Match, Judge, JudgeQualification, Score
from .forms import CompetitionForm


def home(request):
    return render(request, 'competition/home.html')


class CompetitionListView(ListView):
    model = Competition
    template_name = 'competition/competition_list.html'
    context_object_name = 'competitions'

    def get_queryset(self):
        # Filter competitions based on your criteria
        return Competition.objects.all()  # You can adjust this queryset as needed


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'competition/competition_detail.html'


class CompetitionCreateView(CreateView):
    model = Competition
    form_class = CompetitionForm
    template_name = 'competition/competition_create.html'
    # fields = '__all__'


class MemberListView(ListView):
    model = Member
    template_name = 'competition/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        # Filter members based on your criteria
        return Member.objects.all()  # You can adjust this queryset as needed
