# Generated by Django 4.2 on 2023-11-13 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0005_alter_match_finished'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='round',
            field=models.IntegerField(default=0),
        ),
    ]