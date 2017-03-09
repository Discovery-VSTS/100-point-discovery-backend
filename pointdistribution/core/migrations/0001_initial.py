# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GivenPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('week', models.DateField()),
                ('instance_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GivenPointArchived',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('week', models.DateField()),
                ('date', models.DateField()),
                ('instance_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=30, primary_key=True, serialize=False)),
                ('instance_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PointDistribution',
            fields=[
                ('week', models.DateField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('is_final', models.BooleanField()),
                ('instance_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='pointdistribution',
            unique_together=set([('week', 'instance_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('email', 'instance_id')]),
        ),
        migrations.AddField(
            model_name='givenpointarchived',
            name='from_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_givenpointarchived_fromMember', to='core.Member'),
        ),
        migrations.AddField(
            model_name='givenpointarchived',
            name='to_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_givenpointarchived_toMember', to='core.Member'),
        ),
        migrations.AddField(
            model_name='givenpoint',
            name='from_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_givenpoint_fromMember', to='core.Member'),
        ),
        migrations.AddField(
            model_name='givenpoint',
            name='point_distribution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_points', to='core.PointDistribution'),
        ),
        migrations.AddField(
            model_name='givenpoint',
            name='to_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_givenpoint_toMember', to='core.Member'),
        ),
        migrations.AlterUniqueTogether(
            name='givenpointarchived',
            unique_together=set([('to_member', 'week', 'from_member', 'instance_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='givenpoint',
            unique_together=set([('to_member', 'week', 'from_member', 'instance_id')]),
        ),
    ]
