# Generated by Django 2.1.4 on 2019-02-26 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0003_submission_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='total_submission',
            field=models.IntegerField(default=0),
        ),
    ]