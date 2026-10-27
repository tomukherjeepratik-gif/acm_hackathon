from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=255)
    industry_type = models.CharField(max_length=50, choices=[('CONSTRUCTION', 'Construction Site'), ('EDUCATION', 'Educational Institution')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=[('WORKER', 'Worker'), ('ADMIN', 'Employer/Admin')])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    skills = models.TextField(blank=True, default='')
    language_preference = models.CharField(max_length=10, default='en')
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shifts')
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)
    regular_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if self.check_out:
            duration = (self.check_out - self.check_in).total_seconds() / 3600.0
            duration = max(0.0, duration)
            if duration <= 8.0:
                self.regular_hours = duration
                self.overtime_hours = 0.0
            else:
                self.regular_hours = 8.0
                self.overtime_hours = duration - 8.0
        super().save(*args, **kwargs)

class SafetyReport(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.SET_Null, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default='PENDING', choices=[('PENDING', 'Pending'), ('RESOLVED', 'Resolved')])
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
