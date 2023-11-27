from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from .models import Competition, Member, Match
from django.db.models import Case, When, IntegerField, Count, Prefetch, Q
from datetime import datetime, timedelta
from django.utils.timezone import localtime, now
from django.utils import timezone
from django.shortcuts import render
from .models import Team


def reports_filters(request):
    teams = Team.objects.all()
    return render(request, 'reports/reports_filters.html', {'teams': teams})


def competition_summary_report_pdf(request):
    default_start_date = datetime.now() - timedelta(days=365)
    default_end_date = datetime.now() + timedelta(days=365)

    date_from = request.GET.get('date_from', default_start_date)
    date_to = request.GET.get('date_to', default_end_date)

    if date_from and isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        date_from = default_start_date

    if date_to and isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
    else:
        date_to = default_end_date

    # Fetch your data
    competitions = Competition.objects.annotate(
        num_matches=Count('competitioncategory__match', distinct=True),
        num_teams=Count(
            'competitioncategory__match__matchmember__member__team', distinct=True)
    ).prefetch_related(
        'competitioncategory_set__match_set__judge',
        'competitioncategory_set__match_set__matchmember_set__member'
    ).filter(
        date__range=[date_from, date_to]
    )
    total_matches = competitions.aggregate(Count('competitioncategory__match'))[
        'competitioncategory__match__count']

    # Render the HTML template with your data
    html_string = render_to_string(
        'reports/competition_summary_report_pdf.html', {'competitions': competitions, 'total_matches': total_matches})

    # Convert HTML to PDF
    html = HTML(string=html_string)
    result = html.write_pdf()

    # Create a Django response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=competition_summary_report.pdf'
    response.write(result)
    return response


def member_performance_report_pdf(request):
    default_start_date = datetime.now() - timedelta(days=365)
    default_end_date = datetime.now() + timedelta(days=365)

    date_from = request.GET.get('date_from', default_start_date)
    date_to = request.GET.get('date_to', default_end_date)
    team_id = request.GET.get('team')

    if date_from and isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        date_from = default_start_date

    if date_to and isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
    else:
        date_to = default_end_date

    members = Member.objects.annotate(
        total_matches=Count(
            'matchmember',
            filter=Q(matchmember__match__match_time__range=[
                     date_from, date_to]),
            distinct=True
        ),
        wins=Count(
            Case(
                When(matchmember__status=1, then=1),
                filter=Q(matchmember__match__match_time__range=[
                    date_from, date_to]),
                output_field=IntegerField()
            ),
            distinct=True
        ),
        losses=Count(
            Case(
                When(matchmember__status=2, then=1),
                filter=Q(matchmember__match__match_time__range=[
                    date_from, date_to]),
                output_field=IntegerField()
            ),
            distinct=True
        ),
    )

    if team_id:
        members = members.filter(team_id=team_id)

    members = members.filter(
        matchmember__match__match_time__range=[date_from, date_to]
    )

    total_matches = members.aggregate(Count('matchmember'))[
        'matchmember__count']
    team_name = members[0].team.name if team_id else None

    context = {
        'members': members,
        'report_date': timezone.now().strftime("%Y-%m-%d"),
        'total_matches': total_matches,
        'team_name': team_name if team_id else 'All Teams',
        'date_from': date_from.strftime("%Y-%m-%d"),
        'date_to': date_to.strftime("%Y-%m-%d"),
    }

    html_string = render_to_string(
        'reports/member_performance_report_pdf.html', context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    result = html.write_pdf()

    # Create a Django response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=member_performance_report.pdf'
    response.write(result)
    return response
