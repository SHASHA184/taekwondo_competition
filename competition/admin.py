from django.contrib import admin
from .models import Competition, Team, Coach, Member, Belt, WeightClass, Match, Judge, JudgeQualification, MatchMember, CompetitionCategory
from .forms import MemberForm
from django.contrib.auth.models import User, Group
# Register your models here.
admin.site.register(Competition)
admin.site.register(Team)
# admin.site.register(Coach)
# admin.site.register(Member)
admin.site.register(Belt)
admin.site.register(WeightClass)
admin.site.register(Match)
# admin.site.register(Judge)
admin.site.register(JudgeQualification)
admin.site.register(MatchMember)
admin.site.register(CompetitionCategory)


class MemberAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        print(obj)
        user = User.objects.create(username=obj)
        # Переконайтеся, що така група існує
        group = Group.objects.get(name='Member')
        user.groups.add(group)
        obj.user = user
        super().save_model(request, obj, form, change)


class CoachAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        user = User.objects.create(username=obj.name)
        # Переконайтеся, що така група існує
        group = Group.objects.get(name='Coach')
        user.groups.add(group)
        obj.user = user
        super().save_model(request, obj, form, change)


class JudgeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        user = User.objects.create(username=obj.name)
        # Переконайтеся, що така група існує
        group = Group.objects.get(name='Judge')
        user.groups.add(group)
        obj.user = user
        super().save_model(request, obj, form, change)



admin.site.register(Coach, CoachAdmin)
admin.site.register(Judge, JudgeAdmin)
admin.site.register(Member, MemberAdmin)