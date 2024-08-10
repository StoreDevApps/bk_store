import sys
import os
import importlib
import django
from django.conf import settings


def get_django_project_root(settings_module):
    """
    Obtiene el directorio raíz del proyecto Django usando el módulo de configuración.
    """

    django.setup()

    # Importa el módulo de configuración
    importlib.import_module(settings_module)

    # Obtiene la ubicación del archivo de configuración
    settings_file = settings.__file__

    # Determina el directorio raíz del proyecto
    project_root = os.path.dirname(os.path.dirname(settings_file))
    return project_root


# Nombre del módulo de configuración de Django (ajústalo según tu configuración)
settings_module = "myproject.settings"

# Configura el directorio raíz del proyecto en PYTHONPATH
project_root = get_django_project_root(settings_module)
sys.path.append(project_root)
