# Generated by Django 5.2 on 2025-05-02 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='full_name',
            new_name='name',
        ),
    ]
