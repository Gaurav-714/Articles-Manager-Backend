# Generated by Django 5.1.3 on 2024-12-01 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_remove_category_description_alter_tag_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]