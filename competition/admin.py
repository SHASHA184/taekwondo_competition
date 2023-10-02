from django.contrib import admin
from .models import Competition, Team, Coach, Member, Belt, WeightClass, Match, Judge, JudgeQualification, Score

# Register your models here.
admin.site.register(Competition)
admin.site.register(Team)
admin.site.register(Coach)
admin.site.register(Member)
admin.site.register(Belt)
admin.site.register(WeightClass)
admin.site.register(Match)
admin.site.register(Judge)
admin.site.register(JudgeQualification)
admin.site.register(Score)
