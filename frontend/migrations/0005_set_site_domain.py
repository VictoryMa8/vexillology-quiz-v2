from django.db import migrations


def set_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=1,
        defaults={'domain': 'vexillologists.com', 'name': 'Vexillologists'},
    )


def unset_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=1).update(domain='example.com', name='Example Domain')


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_remove_country_gdp_usd_billions_country_entry_type_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(set_site, reverse_code=unset_site),
    ]
