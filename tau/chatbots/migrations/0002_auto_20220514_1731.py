# Generated by Django 3.1.7 on 2022-05-14 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbots', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatbot',
            old_name='username',
            new_name='user_name',
        ),
        migrations.AddField(
            model_name='chatbot',
            name='user_login',
            field=models.CharField(default='This Cant Be Happening', max_length=255),
            preserve_default=False,
        ),
    ]
