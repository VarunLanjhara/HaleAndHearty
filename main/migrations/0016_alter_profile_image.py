# Generated by Django 3.2.6 on 2021-09-09 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20210909_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.png', upload_to='profile_pics'),
        ),
    ]