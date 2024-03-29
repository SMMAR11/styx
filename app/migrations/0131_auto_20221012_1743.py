# Generated by Django 3.2 on 2022-10-12 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0130_auto_20220805_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tfinanceur',
            name='id_org_fin',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.torganisme'),
        ),
        migrations.AlterField(
            model_name='tmoa',
            name='id_org_moa',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.torganisme'),
        ),
        migrations.AlterField(
            model_name='tprestataire',
            name='id_org_prest',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.torganisme'),
        ),
        migrations.AlterField(
            model_name='tutilisateur',
            name='id_util',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
