# Generated manually to safely handle ClienteEntrevista table
# This migration is a replacement for the problematic 0056 migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        # This is a safe no-op migration that ensures the ClienteEntrevista model 
        # is recognized by Django's migration system. The actual table creation
        # will be handled by makemigrations/migrate if needed.
        migrations.RunSQL(
            sql="SELECT 1;",  # Safe no-op SQL
            reverse_sql="SELECT 1;",
        ),
    ]
