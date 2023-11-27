from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


GENDER_CHOICES = [
    (1, 'Male'),
    (2, 'Female'),
]

ROUND_CHOICES = [
    (1, '1/16'),
    (2, '1/8'),
    (3, '1/4'),
    (4, '1/2'),
    (5, 'Final'),
]

STATUS_CHOICES = [
    (0, 'Not started'),
    (1, 'Win'),
    (2, 'Lose'),
    (3, 'Disqualified'),
]

BASE_RATING = 1000

class Competition(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    finished = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('competition-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class CompetitionCategory(models.Model):
    weight_class = models.ForeignKey('WeightClass', on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    def __str__(self):
        return self.competition.name + ' - ' + self.weight_class.name


class WeightClass(models.Model):
    name = models.CharField(max_length=255)
    weight_from = models.IntegerField()
    weight_to = models.IntegerField()
    years_from = models.IntegerField()
    years_to = models.IntegerField()
    gender = models.IntegerField(choices=GENDER_CHOICES)

    def __str__(self):
        return self.name + ' ' + str(self.weight_from) + '-' + str(self.weight_to) + 'kg'


class Team(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Coach(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name
    
    def clean(self, *args, **kwargs):
        # if coach not in competition category, raise an error
        if self.age < 18:
            raise ValidationError(_('Coach age is too young.'))
        if self.age > 60:
            raise ValidationError(_('Coach age is too old.'))


class Member(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    belt_rank = models.ForeignKey('Belt', on_delete=models.CASCADE)
    weight_class = models.ForeignKey(WeightClass, on_delete=models.CASCADE)
    rating = models.IntegerField(default=BASE_RATING)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name
    
    def clean(self, *args, **kwargs):
        # if member not in competition category, raise an error
        if self.weight_class and (self.age < self.weight_class.years_from or self.age > self.weight_class.years_to):
            raise ValidationError(_('Member age does not fit within the weight class age range.'))
        if self.age < 12:
            raise ValidationError(_('Member age is too young.'))
        if self.age > 45:
            raise ValidationError(_('Member age is too old.'))

class Belt(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.color} {self.name}'


class Judge(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    qualification = models.ForeignKey(
        'JudgeQualification', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name
    
    def clean(self, *args, **kwargs):
        # if judge not in competition category, raise an error
        if self.age < 18:
            raise ValidationError(_('Judge age is too young.'))
        if self.age > 60:
            raise ValidationError(_('Judge age is too old.'))


class JudgeQualification(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Match(models.Model):
    match_time = models.DateTimeField()
    finished = models.BooleanField(default=False)
    competition_category = models.ForeignKey(
        CompetitionCategory, on_delete=models.CASCADE)
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    round = models.IntegerField(default=1, choices=ROUND_CHOICES)

    def clean(self, *args, **kwargs):
        # if match_time less than competition date, raise an error
        if self.match_time < self.competition_category.competition.date:
            raise ValidationError(
                _('Match time cannot be less than competition date'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class MatchMember(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    def clean(self, *args, **kwargs):
        # if member not in competition category, raise an error
        if self.match.competition_category.weight_class != self.member.weight_class:
            raise ValidationError(
                _('Member not in competition category'))

    class Meta:
        # Add a unique together constraint to ensure a member cannot be in the same match twice
        unique_together = ('match', 'member')
