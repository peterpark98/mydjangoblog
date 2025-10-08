import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Post
from accounts.models import Profile

class Command(BaseCommand):
    help = '扫描并清理 media 文件夹中未被引用的文件。'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='列出将要被删除的文件，但实际上不执行删除操作。'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.NOTICE('=== 开始扫描媒体文件 ==='))

        # 1. 从数据库中获取所有被引用的文件路径
        referenced_files = set()

        # 从 Profile 的 image 字段获取
        for profile in Profile.objects.exclude(image__isnull=True).exclude(image__exact=''):
            # 排除默认头像
            if profile.image and 'default.jpg' not in profile.image.name:
                referenced_files.add(os.path.normpath(profile.image.path))

        # 从 Post 的特色图片(image)字段获取
        for post in Post.objects.exclude(image__isnull=True).exclude(image__exact=''):
            if post.image:
                referenced_files.add(os.path.normpath(post.image.path))
            
        # 从 Post 的正文(content)字段中解析 CKEditor 上传的图片
        media_url = settings.MEDIA_URL
        # 正则表达式，用于匹配 <img ... src="/media/..." ...> 中的 URL
        img_pattern = re.compile(r'<img[^>]+src="(' + re.escape(media_url) + r'[^"]+)"')
        
        for post in Post.objects.all():
            found_urls = img_pattern.findall(post.content)
            for url in found_urls:
                # 将 URL 转换为服务器上的绝对文件路径
                relative_path = url[len(media_url):]
                file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                referenced_files.add(os.path.normpath(file_path))

        self.stdout.write(f'在数据库中找到了 {len(referenced_files)} 个被引用的文件。')

        # 2. 遍历 media 文件夹，获取磁盘上所有的文件路径
        files_on_disk = set()
        for root, _, files in os.walk(settings.MEDIA_ROOT):
            for filename in files:
                # 再次确认不将默认头像作为清理对象
                if 'default.jpg' in filename:
                    continue
                files_on_disk.add(os.path.normpath(os.path.join(root, filename)))

        self.stdout.write(f'在 media 文件夹中找到了 {len(files_on_disk)} 个文件。')

        # 3. 计算出未被引用的文件
        unreferenced_files = files_on_disk - referenced_files

        if not unreferenced_files:
            self.stdout.write(self.style.SUCCESS('恭喜！没有任何未被引用的文件。'))
            return

        self.stdout.write(self.style.WARNING(f'发现了 {len(unreferenced_files)} 个未被引用的文件：'))

        # 4. 执行删除或打印列表
        deleted_count = 0
        for file_path in sorted(list(unreferenced_files)):
            relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            if dry_run:
                self.stdout.write(f'[演习模式] 将删除: {relative_file_path}')
            else:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    self.stdout.write(f'已删除: {relative_file_path}')
                except OSError as e:
                    self.stdout.write(self.style.ERROR(f'删除失败 {relative_file_path}: {e}'))
        
        # 5. 清理空文件夹
        if not dry_run:
            self.stdout.write(self.style.NOTICE('=== 开始清理空文件夹 ==='))
            for root, dirs, files in os.walk(settings.MEDIA_ROOT, topdown=False):
                if not dirs and not files and root != settings.MEDIA_ROOT:
                    try:
                        os.rmdir(root)
                        self.stdout.write(f'已删除空文件夹: {os.path.relpath(root, settings.MEDIA_ROOT)}')
                    except OSError as e:
                        self.stdout.write(self.style.ERROR(f'删除空文件夹失败 {root}: {e}'))

        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n演习完成，没有文件被实际删除。'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n清理完成！共删除了 {deleted_count} 个文件。'))