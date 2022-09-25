from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.conf import settings


def populate_groups(apps, schema_editor):
    """
    This function is run in migrations/0001_initial_data.py as an initial
    data migration at project initialization. it sets up some basic model-level
    permissions for different groups when the project is initialised.
    """

    # Create user groups
    for name in settings.VALID_GROUPS:
        Group.objects.get_or_create(name=name)

    # Permissions have to be created before applying them
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    # Assign admin permissions
    all_perms = Permission.objects.all()
    admin_perms = [i for i in all_perms]
    Group.objects.get(name="Admin").permissions.add(*admin_perms)

    # For each role assign a propper permission from a dictionary
    # Editor_permission = {Add_question, Add_point, etc...}
    # [i for i in all_perms if i.codename in dictionary]


