# Generated by Django 3.0.7 on 2020-08-13 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_bid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Closedbid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=64)),
                ('winner', models.CharField(max_length=64)),
                ('listingid', models.IntegerField()),
                ('winprice', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='listing',
            name='link',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
    ]
