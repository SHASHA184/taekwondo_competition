from typing import Any
from django import forms
from .models import *
from django.forms import HiddenInput, SelectDateWidget, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Form for the Competition model
class CompetitionForm(forms.ModelForm):
    weight_classes = forms.ModelMultipleChoiceField(
        queryset=WeightClass.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Competition
        fields = ['name', 'location', 'date', 'finished']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(CompetitionForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.fields['weight_classes'].initial = self.instance.competitioncategory_set.values_list(
                'weight_class__pk', flat=True)

    def save(self, commit=True):
        # Save the competition instance
        competition = super(CompetitionForm, self).save(commit=commit)
        if commit:
            # If the instance is saved, update the categories
            competition.competitioncategory_set.all().delete()  # Clear all current categories
            weight_classes = self.cleaned_data.get('weight_classes')
            for weight_class in weight_classes:
                CompetitionCategory.objects.create(
                    competition=competition, weight_class=weight_class)
        return competition

# Form for the CompetitionCategory model


class CompetitionCategoryForm(forms.ModelForm):
    class Meta:
        model = CompetitionCategory
        fields = ['weight_class']


# Formset for the CompetitionCategory model related to the Competition model
CompetitionCategoryFormSet = inlineformset_factory(
    Competition,
    CompetitionCategory,
    form=CompetitionCategoryForm,
    fields=['weight_class'],
    extra=1,  # The number of empty forms to display
    can_delete=True  # Whether to allow deleting formsets
)


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        # all fields except weight_class
        exclude = ('rating',)


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['match_time', 'competition_category', 'judge', 'round']
        widgets = {
            'match_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)


class MatchMemberForm(forms.ModelForm):
    class Meta:
        model = MatchMember
        fields = ['member', 'score', 'status']

    def __init__(self, *args, **kwargs):
        members_queryset = kwargs.pop('members_queryset', None)
        super(MatchMemberForm, self).__init__(*args, **kwargs)

        if members_queryset is not None:
            self.fields['member'].queryset = members_queryset

        # Set 'score' and 'status' fields as not required
        self.fields['score'].required = False
        self.fields['status'].required = False

        if not self.instance.pk:  # Check if this is a new instance
            self.fields['score'].widget = HiddenInput()
            self.fields['status'].widget = HiddenInput()
            self.fields['score'].initial = 0
            self.fields['status'].initial = 0  # Assuming 0 represents 'Not started'
        


MatchMemberFormSet = forms.inlineformset_factory(
    Match, MatchMember, form=MatchMemberForm, max_num=2, extra=2, can_delete=False
)


class CompetitionCategoryForm(forms.ModelForm):
    class Meta:
        model = CompetitionCategory
        fields = '__all__'


class WeightClassForm(forms.ModelForm):
    class Meta:
        model = WeightClass
        fields = '__all__'


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'


class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = '__all__'


class BeltForm(forms.ModelForm):
    class Meta:
        model = Belt
        fields = '__all__'


class JudgeForm(forms.ModelForm):
    class Meta:
        model = Judge
        fields = '__all__'


class JudgeQualificationForm(forms.ModelForm):
    class Meta:
        model = JudgeQualification
        fields = '__all__'


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'location']


# Assuming a team can have multiple members and coaches
MemberFormSet = inlineformset_factory(
    Team, Member, fields=('full_name', 'age', 'gender', 'belt_rank', 'weight_class', 'rating'), extra=1, can_delete=True
)

CoachFormSet = inlineformset_factory(
    Team, Coach, fields=('full_name', 'age'), extra=1, can_delete=True
)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user