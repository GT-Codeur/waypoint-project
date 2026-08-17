# trails/apps.py
from django.apps import AppConfig

class TrailsConfig(AppConfig):    # <-- 3. 'TrailsConfig' (The class name)
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trails'