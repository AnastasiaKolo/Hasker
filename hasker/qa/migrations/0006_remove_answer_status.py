# Generated by Django 5.0.6 on 2024-07-08 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0005_alter_answer_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='status',
        ),
    ]
