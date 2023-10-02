from django.db import models
# Create your models here.


class Competition(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date = models.DateTimeField()
    finished = models.BooleanField(default=False)
    first_place = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='first_place',
        null=True, blank=True)
    second_place = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='second_place',
        null=True, blank=True)
    third_place = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='third_place',
        null=True, blank=True)


class Team(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)


class Coach(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Member(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    belt_rank = models.ForeignKey('Belt', on_delete=models.CASCADE)
    weight_class = models.ForeignKey('WeightClass', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    competitions = models.ManyToManyField(
        Competition, through='CompetitionMembership')


class Belt(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100)


class WeightClass(models.Model):
    name = models.CharField(max_length=100)
    weight_from = models.IntegerField()
    weight_to = models.IntegerField()


class Match(models.Model):
    member1 = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='member1')
    member2 = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='member2')
    match_time = models.DateTimeField()
    finished = models.BooleanField(default=False)
    winner = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='winner')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)


class Judge(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    qualification = models.ForeignKey(
        'JudgeQualification', on_delete=models.CASCADE)


class JudgeQualification(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


class Score(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    member1_score = models.IntegerField()
    member2_score = models.IntegerField()
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)


class CompetitionMembership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)


class JudgeMembership(models.Model):
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
