# Generated by Django 2.1.5 on 2019-03-09 16:07

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_remove_blogpage_intro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpagegalleryimage',
            name='caption',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]