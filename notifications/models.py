from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="接收者")
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions', verbose_name="发起者")
    verb = models.CharField(max_length=255, verbose_name="动作")
    
    # 使用 GenericForeignKey 来指向任何其他模型对象 (如 Post 或 Comment)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    # 已读状态
    read = models.BooleanField(default=False, verbose_name="已读")
    # 通知时间
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间戳")

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = "通知"
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.target:
            return f'{self.actor.username} {self.verb} {self.target}'
        return f'{self.actor.username} {self.verb}'