from django.db.models.signals import post_save
from django.dispatch import receiver
from blog.models import Comment
from .models import Notification

@receiver(post_save, sender=Comment)
def create_notification_on_comment(sender, instance, created, **kwargs):
    # 只在新建评论时触发
    if created:
        comment = instance

        # 情况一：有人评论了你的文章
        if comment.parent is None:
            # 确保不是自己评论自己
            if comment.user != comment.post.author:
                Notification.objects.create(
                    recipient=comment.post.author,
                    actor=comment.user,
                    verb='评论了你的文章',
                    target=comment.post
                )
        
        # 情况二：有人回复了你的评论
        else:
            # 确保不是自己回复自己
            if comment.user != comment.parent.user:
                Notification.objects.create(
                    recipient=comment.parent.user,
                    actor=comment.user,
                    verb='回复了你的评论',
                    target=comment
                )