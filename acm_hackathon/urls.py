from django.contrib import admin
from django.urls import path
import views  # Imports directly from the root views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/checkin/', views.checkin_action, name='checkin'),
    path('dashboard/checkout/', views.checkout_action, name='checkout'),
    path('dashboard/feedback/', views.feedback_action, name='feedback'),
]
