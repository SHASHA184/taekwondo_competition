"""
URL configuration for taekwondo_competition project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from competition.views import *
from competition.reports import *
from competition.statistic import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('generate-matches/', generate_matches, name='generate-matches'),

    path('reports/filters/', reports_filters, name='reports_filters'),
    path('reports/competition-summary-pdf/', competition_summary_report_pdf,
         name='competition_summary_report_pdf'),
    path('reports/member-performance-pdf/', member_performance_report_pdf,
         name='member_performance_report_pdf'),

    path('competition-statistics/', competition_stats,
         name='competition-statistics'),
    path('member-statistics/', member_stats, name='member-statistics'),
    path('match-statistics/', match_stats, name='match-statistics'),
    path('team_statistics/', team_stats, name='team-statistics'),


    path('competitions/', competition_list, name='competitions-list'),
    path('competition/<int:pk>/', CompetitionDetailView.as_view(),
         name='competition-detail'),
    path('competition/create/', CompetitionCreateView.as_view(),
         name='competition-create'),
    path('competition/<int:competition_id>/edit/', competition_edit,
         name='competition-edit'),
    path('competition/<int:competition_id>/delete/', competition_delete,
         name='competition-delete'),


    path('members/', member_list, name='members-list'),
    path('member/create/', member_create,
         name='member-create'),
    path('member/<int:pk>/edit/', member_edit,
         name='member-edit'),
    path('member/<int:pk>/', MemberDetailView.as_view(),
         name='member-detail'),
    path('member/<int:member_id>/delete/', member_delete,
         name='member-delete'),

    path('matches/', match_list, name='matches-list'),
    path('match/create/', match_create,
         name='match-create'),
    path('match/<int:pk>/edit/', match_edit,
         name='match-edit'),
    path('match/<int:pk>/', match_detail,
         name='match-detail'),
    path('match/<int:match_id>/delete/', match_delete,
         name='match-delete'),


    path('judges/', JudgeListView.as_view(), name='judges-list'),
    path('judge/create/', JudgeCreateView.as_view(),
         name='judge-create'),
    path('judge/<int:pk>/edit/', judge_edit,
         name='judge-edit'),
    path('judge/<int:pk>/', JudgeDetailView.as_view(),
         name='judge-detail'),
    path('judge/<int:judge_id>/delete/', judge_delete,
         name='judge-delete'),

    path('teams/', team_list, name='teams-list'),
    path('team/create/', TeamCreateView.as_view(),
         name='team-create'),
    path('team/<int:pk>/', TeamDetailView.as_view(),
         name='team-detail'),
    path('team/<int:pk>/edit/', edit_team,
         name='team-edit'),
    path('team/<int:team_id>/delete/', team_delete,
         name='team-delete'),

    path('qualifications/', JudgeQualificationListView.as_view(),
         name='qualification-list'),
    path('qualification/create/', JudgeQualificationCreateView.as_view(),
         name='qualification-create'),
    path('qualification/<int:pk>/edit/', judge_qualification_edit,
         name='qualification-edit'),
    path('qualification/<int:qualification_id>/delete/', judge_qualification_delete,
         name='qualification-delete'),

    path('coaches/', CoachListView.as_view(),
         name='coaches-list'),
    path('coach/create/', CoachCreateView.as_view(),
         name='coach-create'),
    path('coach/<int:pk>/edit/', coach_edit,
         name='coach-edit'),
    path('coach/<int:pk>/', CoachDetailView.as_view(),
         name='coach-detail'),
    path('coach/<int:coach_id>/delete/', coach_delete,
         name='coach-delete'),
]
