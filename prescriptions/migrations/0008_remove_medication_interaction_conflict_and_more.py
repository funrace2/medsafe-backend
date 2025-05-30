# Generated by Django 5.2 on 2025-05-05 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescriptions', '0007_medication_interaction_conflict_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medication',
            name='interaction_conflict',
        ),
        migrations.RemoveField(
            model_name='medication',
            name='interaction_conflict_info',
        ),
        migrations.AddField(
            model_name='medication',
            name='interaction_warnings',
            field=models.JSONField(blank=True, default=list, help_text='[{new, old, keyword, score, direction}, …] 형태의 충돌 경고 리스트'),
        ),
    ]
