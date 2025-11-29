# Generated manually to simplify Resume model
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_vacancy_company'),
    ]

    operations = [
        # Remove all unnecessary fields
        migrations.RemoveField(
            model_name='resume',
            name='desired_position',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='location',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='email',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='salary_expectation',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='experience_years',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='about',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='skills',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='updated_at',
        ),
        # Update file field with validator
        migrations.AlterField(
            model_name='resume',
            name='file',
            field=models.FileField(
                help_text='Upload PDF or Word document (.pdf, .doc, .docx)',
                upload_to='resumes/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
            ),
        ),
    ]

