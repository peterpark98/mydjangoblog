# django-blog/notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('clear/', views.clear_notifications, name='clear_notifications'),
]