# Generated by Django 5.0.6 on 2024-06-27 20:36

import datetime
import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_text', models.CharField(help_text='Enter tags for a question (e.g. Linux, DB, Network etc.)', max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('question_text', models.TextField()),
                ('votes', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='date created')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('votes', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='date created')),
                ('status', models.IntegerField(blank=True, choices=[(0, 'Not checked yet'), (1, 'Correct'), (2, 'Wrong')], default=0, help_text='Answer status')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qa.question')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('tag_text'), name='tag_text_case_insensitive_unique', violation_error_message='Tag already exists (case insensitive match)'),
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(help_text='Select tags for this question', related_name='questions', to='qa.tag'),
        ),
    ]
