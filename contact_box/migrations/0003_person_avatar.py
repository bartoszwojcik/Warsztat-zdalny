# Generated by Django 2.0.7 on 2018-08-02 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact_box', '0002_auto_20180801_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='avatar',
            field=models.ImageField(null=True, upload_to='media/'),
        ),
    ]
