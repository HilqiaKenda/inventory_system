# Generated by Django 5.1.1 on 2024-10-17 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='email',
            field=models.EmailField(default='example@example.com', max_length=100),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='phone',
            field=models.CharField(default='000-000-0000', max_length=15),
        ),
    ]