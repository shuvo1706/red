# Generated by Django 5.0.6 on 2024-06-03 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_employees', '0002_evaluation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desigid', models.IntegerField()),
                ('designame', models.CharField(max_length=40)),
                ('desigshortname', models.CharField(max_length=40)),
            ],
        ),
    ]
