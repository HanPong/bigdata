# Generated by Django 2.2.6 on 2019-12-22 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moments', '0002_auto_20191124_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatuser',
            name='email',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
