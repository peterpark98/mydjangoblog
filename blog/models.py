from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
import os 
import time 
import random 
from myblog.image_utils import compress_image

# 自定义上传路径函数 ====================
def post_image_path(instance, filename):
    """
    生成唯一的、不包含用户原始文件名的特色图片路径。
    格式: post_images/post_[作者ID]_[时间戳]_[随机数].[ext]
    """
    # 获取文件扩展名
    ext = filename.split('.')[-1].lower()
    # 生成一个基于毫秒时间戳和6位随机字符串的唯一文件名
    timestamp = int(time.time() * 1000)
    random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    
    # 使用作者ID作为文件名前缀，提高可读性和组织性
    author_id = instance.author.pk if instance.author else 'unknown' 
    new_filename = f"post_{author_id}_{timestamp}_{random_str}.{ext}"
    return os.path.join('post_images', new_filename)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    
    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('blog:category_posts', args=[self.slug])

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (('draft', '草稿'), ('published', '已发布'),)
    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=200, unique_for_date='publish', verbose_name="Slug", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name="作者")
    content = CKEditor5Field('正文', config_name='default')
    publish = models.DateTimeField(default=timezone.now, verbose_name="发布时间")
    created = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name="分类")
    image = models.ImageField(upload_to=post_image_path, blank=True, null=True, verbose_name="特色图片")
    views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    
    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ('-publish',)

    def get_absolute_url(self):
        local_publish_time = timezone.localtime(self.publish)
        return reverse('blog:post_detail', args=[
            local_publish_time.year,
            local_publish_time.month,
            local_publish_time.day,
            self.slug
        ])

    def save(self, *args, **kwargs):
        # 自动生成 Slug (如果为空)
        if not self.slug:
            self.slug = slugify(self.title) or "post"
        # 准备检查重复项
        original_slug = self.slug
        queryset = Post.objects.filter(
            publish__date=self.publish.date(),
            slug=self.slug
        )

        # 如果是更新现有文章，必须把自己排除在检查之外，避免与自身冲突
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        # 循环检查，直到 slug 变得唯一
        counter = 1
        while queryset.exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
            # 重新构建查询集以检查新的 slug
            queryset = Post.objects.filter(
                publish__date=self.publish.date(),
                slug=self.slug
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
        
        # 调用我们之前的图片压缩逻辑
        if self.image and hasattr(self.image.file, 'content_type'):
            new_filename, compressed_image_file = compress_image(self.image.file)
            self.image.file = compressed_image_file
            base_name = os.path.splitext(self.image.name)[0]
            self.image.name = f"{base_name}.jpg"

        # 调用父类的 save 方法
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="文章")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments', verbose_name="用户")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    content = models.TextField(verbose_name="评论内容")
    created_on = models.DateTimeField(verbose_name="评论时间", default=timezone.now)
    active = models.BooleanField(default=True, verbose_name="是否激活")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        ordering = ['created_on']

    def get_absolute_url(self):
        """
        返回评论所在文章的 URL，并附带一个指向该评论ID的锚点。
        """
        return f"{self.post.get_absolute_url()}#comment-{self.pk}"

    def get_all_replies(self):
        replies = []
        children = self.replies.filter(active=True).select_related('user__profile', 'parent__user__profile')
        for child in children:
            replies.append(child)
            replies.extend(child.get_all_replies())
        return replies

    def __str__(self):
        return f'对《{self.post.title}》的评论'