# Generated by Django 5.0.6 on 2024-06-20 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.CharField(choices=[('assigned', 'Assigned'), ('started', 'Started'), ('in progress', 'In Progress'), ('bug', 'Bug'), ('completed', 'Completed'), ('commented', 'Commented')], default='assigned', max_length=15),
        ),
        migrations.AlterField(
            model_name='task',
            name='stage',
            field=models.CharField(choices=[('todo', 'To Do'), ('in progress', 'In Progress'), ('completed', 'Completed')], default='todo', max_length=15),
        ),
    ]
