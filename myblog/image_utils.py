# django-blog/myblog/image_utils.py

import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

def compress_image(uploaded_image, target_mb=1, quality=90, min_quality=20):
    """
    压缩图片至指定大小（MB）以下。
    ... (此函数内容保持不变) ...
    """
    target_bytes = target_mb * 1024 * 1024
    
    image = Image.open(uploaded_image)

    if image.mode in ('RGBA', 'LA'):
        image = image.convert('RGB')

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=quality)
    
    if buffer.tell() <= target_bytes:
        filename_base = os.path.splitext(uploaded_image.name)[0]
        new_filename = f"{filename_base}.jpg"
        return new_filename, ContentFile(buffer.getvalue())

    buffer = BytesIO()
    current_quality = quality
    while current_quality > min_quality:
        buffer.seek(0)
        buffer.truncate()
        image.save(buffer, format='JPEG', quality=current_quality)
        
        if buffer.tell() <= target_bytes:
            break
        
        current_quality -= 5

    filename_base = os.path.splitext(uploaded_image.name)[0]
    new_filename = f"{filename_base}.jpg"
    
    return new_filename, ContentFile(buffer.getvalue())


def ckeditor_image_processing(file, request):
    """
    CKEditor 5 的图片处理后端。
    """
    new_filename, compressed_file_obj = compress_image(file)
    return new_filename, compressed_file_obj