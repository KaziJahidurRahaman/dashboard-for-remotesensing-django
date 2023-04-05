# Generated by Django 4.1.7 on 2023-03-30 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ds4rs_app1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NdbiTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fromDate', models.CharField(max_length=255)),
                ('toDate', models.CharField(max_length=255)),
                ('cloudCover', models.CharField(max_length=5)),
                ('satelliteName', models.CharField(max_length=255)),
                ('aoiShape', models.FileField(upload_to='shapefile/')),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='UploadedFile',
        ),
    ]