from django.db import models
from django.utils import timezone
import json


class ClientNode(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('training', 'Training'),
        ('offline', 'Offline'),
    ]
    name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=50, default='127.0.0.1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    local_samples = models.IntegerField(default=0)
    local_accuracy = models.FloatField(default=0.0)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FederatedRound(models.Model):
    round_number = models.IntegerField(unique=True)
    global_accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    participating_clients = models.IntegerField(default=0)
    aggregation_time = models.FloatField(default=0.0)  # seconds
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Round {self.round_number}"

    class Meta:
        ordering = ['round_number']


class AttackLog(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    ATTACK_TYPES = [
        ('DoS', 'Denial of Service'),
        ('Port Scan', 'Port Scan'),
        ('Brute Force', 'Brute Force'),
        ('Botnet', 'Botnet'),
        ('Normal', 'Normal Traffic'),
        ('SQL Injection', 'SQL Injection'),
        ('XSS', 'Cross-Site Scripting'),
    ]
    client = models.ForeignKey(ClientNode, on_delete=models.CASCADE, related_name='attack_logs')
    attack_type = models.CharField(max_length=50, choices=ATTACK_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    probability = models.FloatField(default=0.0)
    source_ip = models.CharField(max_length=50, blank=True)
    destination_ip = models.CharField(max_length=50, blank=True)
    protocol = models.CharField(max_length=20, blank=True)
    bytes_transferred = models.IntegerField(default=0)
    duration = models.FloatField(default=0.0)
    federated_round = models.ForeignKey(FederatedRound, on_delete=models.SET_NULL, null=True, blank=True)
    detected_at = models.DateTimeField(default=timezone.now)
    raw_features = models.TextField(blank=True)  # JSON string of features

    def __str__(self):
        return f"{self.attack_type} on {self.client.name} at {self.detected_at}"

    class Meta:
        ordering = ['-detected_at']


class ModelPerformance(models.Model):
    federated_round = models.OneToOneField(FederatedRound, on_delete=models.CASCADE, related_name='performance')
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    true_positives = models.IntegerField(default=0)
    true_negatives = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    false_negatives = models.IntegerField(default=0)
    confusion_matrix = models.TextField(blank=True)  # JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Performance Round {self.federated_round.round_number}"


class TrainingSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rounds = models.IntegerField(default=10)
    current_round = models.IntegerField(default=0)
    participating_clients = models.ManyToManyField(ClientNode, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    config = models.TextField(blank=True)  # JSON config

    def __str__(self):
        return f"Session {self.id} - {self.status}"
