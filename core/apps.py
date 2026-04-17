# from django.apps import AppConfig

# class FedsecureConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'fedsecure'

#     def ready(self):
#         # Connect signals after app is ready
#         from .signals import connect_training_signal
#         connect_training_signal()



# core/apps.py
# from django.apps import AppConfig

# class CoreConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'core'  # must match your folder name

#     def ready(self):
#         from .signals import connect_training_signal
#         connect_training_signal()
        
        



from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Prevent duplicate execution
        if os.environ.get('RUN_MAIN') != 'true':
            return

        # Keep your existing signal
        from .signals import connect_training_signal
        connect_training_signal()

        # ✅ Create default demo user
        from django.contrib.auth.models import User

        if not User.objects.filter(username='analyst').exists():
            User.objects.create_user(
                username='analyst',
                password='analyst123'
            )