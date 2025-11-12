# Generated migration for multiple programs support

from django.db import migrations, models
import django.db.models.deletion


def migrate_single_to_multiple_programs(apps, schema_editor):
    """Migrate existing single program assignments to multiple programs"""
    TrainerProfile = apps.get_model('Applicant', 'TrainerProfile')
    
    for trainer in TrainerProfile.objects.all():
        if trainer.program:
            # Add the existing program to the new ManyToMany field
            trainer.programs.add(trainer.program)


class Migration(migrations.Migration):

    dependencies = [
        ('Applicant', '0054_programapplication_is_under_review_and_more'),  # Latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='trainerprofile',
            name='programs',
            field=models.ManyToManyField(blank=True, related_name='trainers', to='Applicant.Programs'),
        ),
        migrations.AlterField(
            model_name='trainerprofile',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='legacy_trainers', to='Applicant.programs'),
        ),
        migrations.RunPython(migrate_single_to_multiple_programs, migrations.RunPython.noop),
    ]
