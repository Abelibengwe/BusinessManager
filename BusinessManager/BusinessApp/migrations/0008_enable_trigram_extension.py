# Migration to enable PostgreSQL extensions for better performance
from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('BusinessApp', '0007_add_django_indexes'),
    ]

    operations = [
        # Enable trigram extension for better text search performance
        TrigramExtension(),
    ]
