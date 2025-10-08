from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.contrib.auth.decorators import login_required

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        # 只获取当前登录用户的通知
        return self.request.user.notifications.all()
    
    def get(self, request, *args, **kwargs):
        # 当用户访问此页面时，将所有未读通知标记为已读
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return super().get(request, *args, **kwargs)
@login_required
def clear_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user).delete()
    return redirect('notifications:notification_list')