# Generated by Django 5.2 on 2025-05-02 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescriptions', '0004_allergy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='hospital_name',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='pharmacy_name',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='pharmacy_phone',
        ),
        migrations.AddField(
            model_name='medication',
            name='hospital_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='병원 이름'),
        ),
        migrations.AddField(
            model_name='medication',
            name='pharmacy_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='약국명'),
        ),
        migrations.AddField(
            model_name='medication',
            name='pharmacy_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='약국 전화번호'),
        ),
    ]
