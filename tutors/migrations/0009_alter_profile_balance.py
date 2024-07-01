# Generated by Django 5.0.6 on 2024-06-23 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutors', '0008_profile_purchased_books_delete_purchase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=5000.0, max_digits=10),
        ),
    ]
