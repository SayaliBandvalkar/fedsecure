from django.contrib import admin
from .models import ClientNode, FederatedRound, AttackLog, ModelPerformance, TrainingSession

@admin.register(ClientNode)
class ClientNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'status', 'local_samples', 'local_accuracy', 'last_seen']
    list_filter = ['status']

@admin.register(FederatedRound)
class FederatedRoundAdmin(admin.ModelAdmin):
    list_display = ['round_number', 'global_accuracy', 'precision', 'recall', 'f1_score', 'participating_clients']

@admin.register(AttackLog)
class AttackLogAdmin(admin.ModelAdmin):
    list_display = ['client', 'attack_type', 'severity', 'probability', 'detected_at']
    list_filter = ['attack_type', 'severity', 'client']

@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['federated_round', 'accuracy', 'precision', 'recall', 'f1_score']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'total_rounds', 'current_round', 'started_at']
