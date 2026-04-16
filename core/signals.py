# # signals.py

# from django.db.models.signals import post_save

# def auto_start_training(sender, instance, created, **kwargs):
#     if created:
#         # Relative imports to avoid Pylance errors
#         from .models import TrainingSession
#         from .federated import run_federated_simulation

#         if not isinstance(instance, TrainingSession):
#             return

#         if instance.status != 'completed':
#             rounds = getattr(instance, 'total_rounds', 5)

#             instance.status = 'running'
#             instance.save(update_fields=['status'])

#             run_federated_simulation(rounds)

#             instance.status = 'completed'
#             instance.save(update_fields=['status'])


# def connect_training_signal():
#     from .models import TrainingSession
#     post_save.connect(auto_start_training, sender=TrainingSession)








from django.db.models.signals import post_save

def auto_start_training(sender, instance, created, **kwargs):
    """
    Automatically starts federated training when a new TrainingSession is created.
    Updates the session in real-time so admin panel reflects progress.
    """
    if created:
        # Relative imports to avoid circular import / Pylance errors
        from .models import TrainingSession
        from .federated import run_federated_simulation

        if not isinstance(instance, TrainingSession):
            return

        if instance.status != 'completed':
            # Set session as running
            instance.status = 'running'
            instance.save(update_fields=['status'])

            # Pass the session ID to the federated simulation
            run_federated_simulation(num_rounds=instance.total_rounds, session_id=instance.id)

            # Mark session as completed
            instance.status = 'completed'
            instance.completed_at = instance.completed_at or None
            instance.save(update_fields=['status', 'completed_at'])


def connect_training_signal():
    from .models import TrainingSession
    post_save.connect(auto_start_training, sender=TrainingSession)