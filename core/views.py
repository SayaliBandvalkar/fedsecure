from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Avg
from .models import ClientNode, FederatedRound, AttackLog, ModelPerformance, TrainingSession
from .federated import run_federated_simulation, predict_attack
import json
import random


# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('dashboard')
#         else:
#             messages.error(request, 'Invalid credentials. Please try again.')
#     return render(request, 'core/login.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔥 Role-based access
            if user.is_superuser:
                return redirect('/admin/')   # Admin → Django admin panel
            else:
                return redirect('dashboard')  # Analyst → your dashboard

        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    clients = ClientNode.objects.all()
    total_clients = clients.filter(status='active').count()
    total_attacks = AttackLog.objects.exclude(attack_type='Normal').count()
    latest_round = FederatedRound.objects.order_by('-round_number').first()
    current_round = latest_round.round_number if latest_round else 0
    global_accuracy = latest_round.global_accuracy if latest_round else 0

    # Chart data
    attack_type_data = {}
    for at in ['DoS', 'Port Scan', 'Brute Force', 'Botnet', 'SQL Injection', 'XSS']:
        attack_type_data[at] = AttackLog.objects.filter(attack_type=at).count()

    # Last 7 days trend
    from datetime import timedelta
    dates = []
    counts = []
    for i in range(6, -1, -1):
        d = timezone.now().date() - timedelta(days=i)
        c = AttackLog.objects.filter(detected_at__date=d).exclude(attack_type='Normal').count()
        dates.append(d.strftime('%b %d'))
        counts.append(c)

    # Round accuracy data
    rounds = FederatedRound.objects.order_by('round_number')
    round_labels = [f"R{r.round_number}" for r in rounds]
    round_accuracies = [r.global_accuracy for r in rounds]

    # Client comparison
    client_names = [c.name for c in clients]
    client_accuracies = [c.local_accuracy for c in clients]

    # Live alerts (recent 5)
    recent_alerts = AttackLog.objects.exclude(attack_type='Normal').select_related('client')[:5]

    context = {
        'total_clients': total_clients,
        'total_attacks': total_attacks,
        'current_round': current_round,
        'global_accuracy': round(global_accuracy, 1),
        'recent_alerts': recent_alerts,
        'attack_type_data': json.dumps(attack_type_data),
        'trend_dates': json.dumps(dates),
        'trend_counts': json.dumps(counts),
        'round_labels': json.dumps(round_labels),
        'round_accuracies': json.dumps(round_accuracies),
        'client_names': json.dumps(client_names),
        'client_accuracies': json.dumps(client_accuracies),
        'active_page': 'dashboard',
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def clients(request):
    all_clients = ClientNode.objects.all().order_by('id')
    context = {
        'clients': all_clients,
        'active_page': 'clients',
    }
    return render(request, 'core/clients.html', context)


@login_required
def federated_training(request):
    rounds = FederatedRound.objects.all().order_by('round_number')
    sessions = TrainingSession.objects.all().order_by('-started_at')[:5]
    all_clients = ClientNode.objects.all()

    round_labels = [f"Round {r.round_number}" for r in rounds]
    round_accuracies = [r.global_accuracy for r in rounds]
    round_precision = [r.precision for r in rounds]
    round_recall = [r.recall for r in rounds]

    context = {
        'rounds': rounds,
        'sessions': sessions,
        'all_clients': all_clients,
        'round_labels': json.dumps(round_labels),
        'round_accuracies': json.dumps(round_accuracies),
        'round_precision': json.dumps(round_precision),
        'round_recall': json.dumps(round_recall),
        'active_page': 'training',
    }
    return render(request, 'core/federated_training.html', context)


@login_required
def intrusion_detection(request):
    prediction = None
    if request.method == 'POST':
        # Manual input
        features = {
            'duration': request.POST.get('duration', 0),
            'bytes': request.POST.get('bytes', 0),
            'packets': request.POST.get('packets', 0),
            'protocol': request.POST.get('protocol', 'TCP'),
            'port': request.POST.get('port', 80),
            'flags': request.POST.get('flags', 0),
        }
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            import io
            content = csv_file.read().decode('utf-8')
            lines = content.strip().split('\n')
            if len(lines) > 1:
                headers = lines[0].split(',')
                vals = lines[1].split(',')
                for h, v in zip(headers, vals):
                    features[h.strip()] = v.strip()

        prediction = predict_attack(features)

    context = {
        'prediction': prediction,
        'active_page': 'detection',
    }
    return render(request, 'core/intrusion_detection.html', context)


@login_required
def attack_logs(request):
    logs = AttackLog.objects.select_related('client').order_by('-detected_at')
    severity_filter = request.GET.get('severity', '')
    type_filter = request.GET.get('type', '')
    client_filter = request.GET.get('client', '')

    if severity_filter:
        logs = logs.filter(severity=severity_filter)
    if type_filter:
        logs = logs.filter(attack_type=type_filter)
    if client_filter:
        logs = logs.filter(client__id=client_filter)

    all_clients = ClientNode.objects.all()
    context = {
        'logs': logs[:200],
        'all_clients': all_clients,
        'severity_filter': severity_filter,
        'type_filter': type_filter,
        'client_filter': client_filter,
        'active_page': 'logs',
    }
    return render(request, 'core/attack_logs.html', context)


@login_required
def performance(request):
    latest_round = FederatedRound.objects.order_by('-round_number').first()
    perf = None
    if latest_round:
        perf = ModelPerformance.objects.filter(federated_round=latest_round).first()

    rounds = FederatedRound.objects.order_by('round_number')
    round_labels = [f"R{r.round_number}" for r in rounds]
    round_accuracies = [r.global_accuracy for r in rounds]
    round_f1 = [r.f1_score for r in rounds]

    # Confusion matrix data from latest
    cm_data = [[85, 5], [3, 92]]
    if perf and perf.confusion_matrix:
        try:
            cm_data = json.loads(perf.confusion_matrix)
        except:
            pass

    context = {
        'perf': perf,
        'latest_round': latest_round,
        'round_labels': json.dumps(round_labels),
        'round_accuracies': json.dumps(round_accuracies),
        'round_f1': json.dumps(round_f1),
        'cm_data': json.dumps(cm_data),
        'active_page': 'performance',
    }
    return render(request, 'core/performance.html', context)


# ---- API Endpoints ----

# @login_required
# @require_POST
# def api_run_training(request):
#     try:
#         data = json.loads(request.body)
#         rounds = int(data.get('rounds', 5))
#         rounds = min(max(rounds, 1), 20)
#         result = run_federated_simulation(rounds)
#         return JsonResponse({'status': 'success', 'result': result})
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def api_run_training(request):
    try:
        data = json.loads(request.body)
        rounds = int(data.get('rounds', 5))
        rounds = min(max(rounds, 1), 20)

        # ✅ CREATE SESSION FIRST
        session = TrainingSession.objects.create(
            status='running',
            total_rounds=rounds,
            current_round=0
        )

        # ✅ PASS session_id
        result = run_federated_simulation(rounds, session.id)

        return JsonResponse({'status': 'success', 'result': result})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_dashboard_stats(request):
    total_clients = ClientNode.objects.filter(status='active').count()
    total_attacks = AttackLog.objects.exclude(attack_type='Normal').count()
    latest_round = FederatedRound.objects.order_by('-round_number').first()
    current_round = latest_round.round_number if latest_round else 0
    global_accuracy = latest_round.global_accuracy if latest_round else 0

    recent = AttackLog.objects.exclude(attack_type='Normal').select_related('client').order_by('-detected_at')[:5]
    alerts = [{'client': a.client.name, 'type': a.attack_type, 'severity': a.severity, 'time': a.detected_at.strftime('%H:%M:%S')} for a in recent]

    return JsonResponse({
        'total_clients': total_clients,
        'total_attacks': total_attacks,
        'current_round': current_round,
        'global_accuracy': round(global_accuracy, 1),
        'alerts': alerts,
    })


@login_required
@require_POST
def api_add_client(request):
    try:
        data = json.loads(request.body)
        client = ClientNode.objects.create(
            name=data.get('name', f'Client {ClientNode.objects.count()+1}'),
            ip_address=data.get('ip', '192.168.1.1'),
            local_samples=random.randint(3000, 8000),
            local_accuracy=round(random.uniform(88, 97), 1),
            status='active',
        )
        return JsonResponse({'status': 'success', 'id': client.id, 'name': client.name})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_simulate_attack(request):
    """Simulate a random attack on a random client"""
    clients = ClientNode.objects.filter(status='active')
    if not clients.exists():
        return JsonResponse({'status': 'error', 'message': 'No active clients'}, status=400)

    client = random.choice(list(clients))
    attack_types = ['DoS', 'Port Scan', 'Brute Force', 'Botnet', 'SQL Injection']
    severities = ['low', 'medium', 'high', 'critical']
    protocols = ['TCP', 'UDP', 'ICMP', 'HTTP']

    attack = AttackLog.objects.create(
        client=client,
        attack_type=random.choice(attack_types),
        severity=random.choice(severities),
        probability=round(random.uniform(0.75, 0.99), 2),
        source_ip=f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        destination_ip=f"10.0.{random.randint(0,10)}.{random.randint(1,50)}",
        protocol=random.choice(protocols),
        bytes_transferred=random.randint(500, 100000),
        duration=round(random.uniform(0.1, 30.0), 2),
    )
    return JsonResponse({
        'status': 'success',
        'attack': {
            'client': client.name,
            'type': attack.attack_type,
            'severity': attack.severity,
            'time': attack.detected_at.strftime('%H:%M:%S'),
        }
    })
