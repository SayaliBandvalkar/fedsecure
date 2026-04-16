# from django.apps import AppConfig

# class FedsecureConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'fedsecure'

#     def ready(self):
#         # Connect signals after app is ready
#         from .signals import connect_training_signal
#         connect_training_signal()



# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'  # must match your folder name

    def ready(self):
        from .signals import connect_training_signal
        connect_training_signal()