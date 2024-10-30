# Generated by Django 4.2.1 on 2024-10-27 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Indicators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('indicators', models.ManyToManyField(blank=True, to='srch.indicators')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('vk_url', models.URLField(blank=True, null=True)),
                ('vk_id', models.CharField(max_length=255, unique=True)),
                ('hh_url', models.URLField(blank=True, null=True)),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='srch.profession')),
            ],
        ),
        migrations.CreateModel(
            name='StaffMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('login', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='srch.staffmembers')),
            ],
        ),
        migrations.CreateModel(
            name='StaffProfilesScores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srch.profile')),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srch.staffmembers')),
            ],
            options={
                'unique_together': {('staff_member', 'profile', 'score')},
            },
        ),
        migrations.CreateModel(
            name='StaffProfessionIndicators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srch.indicators')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srch.profession')),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srch.staffmembers')),
            ],
            options={
                'unique_together': {('staff_member', 'profession', 'indicator')},
            },
        ),
    ]
