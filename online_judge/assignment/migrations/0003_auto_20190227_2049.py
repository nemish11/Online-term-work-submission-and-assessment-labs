# Generated by Django 2.1.4 on 2019-02-27 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0002_auto_20190227_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='deadline',
        ),
        migrations.AlterField(
            model_name='assignment',
            name='total_inputfiles',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assignment_files',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='submission',
            name='commentunread',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='datetime',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='week',
            name='lastdate',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='week',
            name='year',
            field=models.IntegerField(),
        ),
    ]