# Generated by Django 5.0.6 on 2024-08-15 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rate_employees', '0013_remove_award_advisorid_award_created_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='Status',
        ),
        migrations.RemoveField(
            model_name='award',
            name='remark',
        ),
    ]
