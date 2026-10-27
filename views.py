from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import *
from decimal import Decimal
from django.db.models import Sum

def index_view(request):
    return render(request, 'fairshift/index.html')

def login_view(request):
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'fairshift/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def dashboard_view(request):
    profile = request.user.profile
    org = profile.organization
    
    if profile.role == 'WORKER':
        shifts = Shift.objects.filter(user=request.user).order_index = Shift.objects.filter(user=request.user).order_by('-check_in')
        active_shift = Shift.objects.filter(user=request.user, check_out__isnull=True).first()
        
        # Payroll aggregates
        total_reg = Shift.objects.filter(user=request.user, check_out__isnull=False).aggregate(Sum('regular_hours'))['regular_hours__sum'] or 0.0
        total_ot = Shift.objects.filter(user=request.user, check_out__isnull=False).aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0.0
        
        rate = float(profile.hourly_rate)
        total_earnings = (float(total_reg) * rate) + (float(total_ot) * rate * 1.5)
        
        ctx = {
            'profile': profile,
            'shifts': shifts,
            'active_shift': active_shift,
            'total_hours': float(total_reg) + float(total_ot),
            'total_earnings': f"{total_earnings:,.2f}"
        }
    else:
        # Admin View metrics isolated strictly by organization boundary
        workers = UserProfile.objects.filter(organization=org, role='WORKER')
        worker_users = [w.user for w in workers]
        
        shifts = Shift.objects.filter(user__in=worker_users, check_out__isnull=False)
        reg_sum = float(shifts.aggregate(Sum('regular_hours'))['regular_hours__sum'] or 0.0)
        ot_sum = float(shifts.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0.0)
        
        # Organization absolute isolated payroll aggregate
        payroll_agg = 0.0
        for w in workers:
            w_shifts = shifts.filter(user=w.user)
            w_reg = float(w_shifts.aggregate(Sum('regular_hours'))['regular_hours__sum'] or 0.0)
            w_ot = float(w_shifts.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0.0)
            payroll_agg += (w_reg * float(w.hourly_rate)) + (w_ot * float(w.hourly_rate) * 1.5)
            
        items_feedback = Feedback.objects.filter(organization=org).order_by('-created_at')
        
        ctx = {
            'profile': profile,
            'total_workers': workers.count(),
            'aggregate_hours': f"{reg_sum + ot_sum:,.1f}",
            'aggregate_payroll': f"{payroll_agg:,.2f}",
            'items_feedback': items_feedback,
            'regular_sum': reg_sum,
            'overtime_sum': ot_sum
        }
        
    return render(request, 'fairshift/dashboard.html', ctx)

@login_required
def checkin_action(request):
    if request.method == 'POST':
        active = Shift.objects.filter(user=request.user, check_out__isnull=True).exists()
        if not active:
            Shift.objects.create(user=request.user, check_in=timezone.now())
            messages.success(request, 'Successfully checked into shift.')
        else:
            messages.error(request, 'An active shift session is already running.')
    return redirect('/dashboard/')

@login_required
def checkout_action(request):
    if request.method == 'POST':
        active = Shift.objects.filter(user=request.user, check_out__isnull=True).first()
        if active:
            active.check_out = timezone.now()
            active.save()
            messages.success(request, 'Successfully clocked out.')
        else:
            messages.error(request, 'No active shift found to process checkout.')
    return redirect('/dashboard/')

@login_required
def feedback_action(request):
    if request.method == 'POST':
        msg = request.POST.get('message')
        Feedback.objects.create(organization=request.user.profile.organization, message=msg)
        messages.success(request, 'Anonymous operational feedback submitted securely.')
    return redirect('/dashboard/')
