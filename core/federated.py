"""
Federated Learning Simulation Engine for FedSecure
Simulates the FL process without actual network communication.
Each 'client' trains locally and sends model updates (gradients).
The server aggregates using FedAvg algorithm.
"""
import random
import math
import json
from datetime import timedelta
from django.utils import timezone
from .models import TrainingSession


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def softmax(scores):
    exp_scores = [math.exp(s) for s in scores]
    total = sum(exp_scores)
    return [s / total for s in exp_scores]


class LocalModel:
    """Simulates a local ML model on a client node"""
    def __init__(self, client_id, n_samples):
        self.client_id = client_id
        self.n_samples = n_samples
        # Model weights (simplified linear model)
        self.weights = [random.gauss(0, 0.1) for _ in range(10)]
        self.bias = random.gauss(0, 0.05)

    def train(self, rounds=5, lr=0.01):
        """Simulate local training"""
        initial_loss = random.uniform(0.4, 0.8)
        final_loss = initial_loss * random.uniform(0.3, 0.6)
        # Simulate gradient updates
        gradients = []
        for w in self.weights:
            grad = random.gauss(-0.02, 0.005)  # Negative = improving
            self.weights[self.weights.index(w)] += lr * grad
            gradients.append(grad)

        local_accuracy = random.uniform(88, 97)
        return {
            'gradients': gradients,
            'bias_grad': random.gauss(-0.01, 0.003),
            'local_accuracy': round(local_accuracy, 2),
            'loss': round(final_loss, 4),
            'n_samples': self.n_samples,
        }

    def get_weights(self):
        return self.weights[:], self.bias


class FedAvgServer:
    """Federated Averaging Server"""
    def __init__(self):
        self.global_weights = [random.gauss(0, 0.1) for _ in range(10)]
        self.global_bias = 0.0
        self.round_history = []

    def aggregate(self, client_updates):
        """FedAvg: weighted average of client updates"""
        total_samples = sum(u['n_samples'] for u in client_updates)

        new_weights = [0.0] * 10
        new_bias = 0.0

        for update in client_updates:
            weight = update['n_samples'] / total_samples
            for i, grad in enumerate(update['gradients']):
                new_weights[i] += weight * grad
            new_bias += weight * update['bias_grad']

        # Apply aggregated gradients
        lr = 0.01
        for i in range(len(self.global_weights)):
            self.global_weights[i] += lr * new_weights[i]
        self.global_bias += lr * new_bias

        return self.global_weights[:], self.global_bias

    def evaluate(self, round_num):
        """Simulate global model evaluation"""
        # Accuracy increases with rounds (realistic FL curve)
        base = 80.0
        growth = 15.0 * (1 - math.exp(-0.3 * round_num))
        noise = random.gauss(0, 0.5)
        accuracy = min(98.5, base + growth + noise)

        precision = accuracy - random.uniform(0.5, 2.0)
        recall = accuracy - random.uniform(0.5, 2.5)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            'accuracy': round(accuracy, 2),
            'precision': round(precision, 2),
            'recall': round(recall, 2),
            'f1': round(f1, 2),
        }


def run_federated_simulation(num_rounds=5, session_id=None):
    """
    Main simulation function.
    Creates clients, runs FL rounds, saves results to DB.
    """
    from .models import ClientNode, FederatedRound, AttackLog, ModelPerformance
    
     # Get the session to update
    if session_id:
        session = TrainingSession.objects.get(id=session_id)
    else:
        session = TrainingSession.objects.filter(status='running').last()

    if not session:
        return []

    # Reset current_round
    session.current_round = 0
    session.save(update_fields=['current_round'])
    

    #  # Try to get the active TrainingSession
    # session = TrainingSession.objects.filter(status='running').last()
    # if session:
    #     session.current_round = 0
    #     session.total_rounds = num_rounds
    #     session.save(update_fields=['current_round', 'total_rounds'])
    
    # Get or create clients
    clients = list(ClientNode.objects.filter(status__in=['active', 'idle']))
    if not clients:
        # Create default clients
        for i in range(3):
            c = ClientNode.objects.create(
                name=f'Client {i+1}',
                ip_address=f'192.168.1.{10+i}',
                status='active',
                local_samples=random.randint(4000, 6000),
                local_accuracy=random.uniform(88, 94),
            )
            clients.append(c)

    # Determine starting round
    last_round = FederatedRound.objects.order_by('-round_number').first()
    start_round = (last_round.round_number + 1) if last_round else 1

    server = FedAvgServer()
    local_models = {c.id: LocalModel(c.id, c.local_samples) for c in clients}

    results = []

    for r in range(start_round, start_round + num_rounds):
        round_start = timezone.now()

        # Update session current_round in DB
        if session:
            session.current_round = r
            session.save(update_fields=['current_round'])
        
        # Mark clients as training
        ClientNode.objects.filter(id__in=[c.id for c in clients]).update(status='training')

        # Local training on each client
        client_updates = []
        for c in clients:
            model = local_models[c.id]
            update = model.train(rounds=3)
            client_updates.append(update)

            # Update client accuracy in DB
            ClientNode.objects.filter(id=c.id).update(
                local_accuracy=round(update['local_accuracy'], 1),
                last_seen=timezone.now(),
                status='active',
            )

        # Aggregate on server
        server.aggregate(client_updates)

        # Evaluate global model
        metrics = server.evaluate(r)

        # Aggregation time simulation
        agg_time = round(random.uniform(0.5, 3.0) + len(clients) * 0.2, 2)

        # Save round
        fed_round = FederatedRound.objects.create(
            round_number=r,
            global_accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1'],
            participating_clients=len(clients),
            aggregation_time=agg_time,
            started_at=round_start,
            completed_at=timezone.now(),
        )

        # Save performance
        tp = random.randint(80, 100)
        tn = random.randint(80, 100)
        fp = random.randint(1, 10)
        fn = random.randint(1, 10)
        cm = [[tp, fp], [fn, tn]]

        ModelPerformance.objects.create(
            federated_round=fed_round,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1'],
            true_positives=tp,
            true_negatives=tn,
            false_positives=fp,
            false_negatives=fn,
            confusion_matrix=json.dumps(cm),
        )

        # Simulate some attack detections during this round
        attack_types = ['DoS', 'Port Scan', 'Brute Force', 'Botnet', 'SQL Injection', 'XSS', 'Normal']
        severities = ['low', 'medium', 'high', 'critical']
        protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']

        for _ in range(random.randint(3, 8)):
            client = random.choice(clients)
            atype = random.choice(attack_types)
            AttackLog.objects.create(
                client=client,
                attack_type=atype,
                severity=random.choice(severities) if atype != 'Normal' else 'low',
                probability=round(random.uniform(0.70, 0.99), 2),
                source_ip=f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                destination_ip=f"192.168.1.{random.randint(1,50)}",
                protocol=random.choice(protocols),
                bytes_transferred=random.randint(100, 500000),
                duration=round(random.uniform(0.01, 60.0), 2),
                federated_round=fed_round,
            )

        results.append({
            'round': r,
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1'],
            'clients': len(clients),
        })
        
    # Mark session as completed
    if session:
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save(update_fields=['status', 'completed_at'])

    

    return results


ATTACK_SIGNATURES = {
    'DoS': {'min_bytes': 50000, 'min_packets': 500, 'ports': [80, 443, 53]},
    'Port Scan': {'min_packets': 100, 'duration_max': 5, 'ports': list(range(1, 1024))},
    'Brute Force': {'min_packets': 50, 'ports': [22, 21, 3389, 5900]},
    'Botnet': {'min_bytes': 1000, 'ports': [6667, 6668, 6669]},
    'SQL Injection': {'ports': [3306, 5432, 1433], 'protocol': 'TCP'},
    'XSS': {'ports': [80, 443, 8080]},
}


def predict_attack(features):
    """
    Simulated ML prediction using heuristic scoring.
    In production this would use the actual global model weights.
    """
    try:
        duration = float(features.get('duration', 0))
        bytes_val = float(features.get('bytes', 0))
        packets = float(features.get('packets', 0))
        port = int(float(features.get('port', 80)))
        protocol = str(features.get('protocol', 'TCP')).upper()
        flags = int(float(features.get('flags', 0)))
    except (ValueError, TypeError):
        duration, bytes_val, packets, port, protocol, flags = 1, 1000, 10, 80, 'TCP', 0

    scores = {
        'Normal': 0.3,
        'DoS': 0.0,
        'Port Scan': 0.0,
        'Brute Force': 0.0,
        'Botnet': 0.0,
        'SQL Injection': 0.0,
        'XSS': 0.0,
    }

    # Heuristic rules (simulating model behavior)
    if bytes_val > 100000 and packets > 500:
        scores['DoS'] += 0.6
    if bytes_val > 500000:
        scores['DoS'] += 0.3

    if packets > 200 and duration < 5:
        scores['Port Scan'] += 0.5
    if port < 1024 and packets > 100:
        scores['Port Scan'] += 0.2

    if port in [22, 21, 3389, 5900] and packets > 30:
        scores['Brute Force'] += 0.5
    if flags > 5:
        scores['Brute Force'] += 0.2

    if port in [6667, 6668, 6669]:
        scores['Botnet'] += 0.7
    if bytes_val < 5000 and packets > 20 and duration > 30:
        scores['Botnet'] += 0.3

    if port in [3306, 5432, 1433] and protocol == 'TCP':
        scores['SQL Injection'] += 0.6

    if port in [80, 443, 8080] and bytes_val < 2000:
        scores['XSS'] += 0.4

    # Add noise (simulate model uncertainty)
    for k in scores:
        scores[k] += random.gauss(0, 0.05)
        scores[k] = max(0, scores[k])

    # Softmax normalization
    total = sum(scores.values()) or 1
    for k in scores:
        scores[k] = round(scores[k] / total, 4)

    # Get prediction
    predicted = max(scores, key=scores.get)
    confidence = round(scores[predicted] * 100, 1)

    severity = 'low'
    if predicted != 'Normal':
        if confidence > 85:
            severity = 'critical'
        elif confidence > 70:
            severity = 'high'
        elif confidence > 55:
            severity = 'medium'

    return {
        'attack_type': predicted,
        'confidence': confidence,
        'severity': severity,
        'is_attack': predicted != 'Normal',
        'all_scores': {k: round(v * 100, 1) for k, v in scores.items()},
    }
