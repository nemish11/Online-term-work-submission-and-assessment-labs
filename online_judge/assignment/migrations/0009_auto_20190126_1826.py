# Generated by Django 2.1.4 on 2019-01-26 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0008_auto_20190126_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission_files',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]