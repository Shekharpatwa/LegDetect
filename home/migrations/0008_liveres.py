# Generated by Django 4.0.2 on 2022-03-29 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_imageres_remove_liveresult_user_delete_imageresult_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveRes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('LiveLeftAngle', models.CharField(max_length=255)),
                ('LiveRightAngle', models.CharField(max_length=255)),
                ('date', models.DateField()),
            ],
        ),
    ]
