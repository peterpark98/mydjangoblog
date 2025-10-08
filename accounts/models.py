from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(
        max_length=50,
        verbose_name='昵称',
        unique=True,
        error_messages={
            'unique': "该昵称已被占用，请换一个。",
        }
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    location = models.CharField(max_length=30, blank=True, verbose_name='所在地')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics', verbose_name='头像')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} 的资料'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    当 User 对象被创建时，自动创建对应的 Profile；
    当 User 对象被保存时，确保其 Profile 也被保存。
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()