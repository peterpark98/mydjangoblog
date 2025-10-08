from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import home
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('', home, name='home'),
    path('blog/', include('blog.urls', namespace='blog')),
    # CKEditor 5 自定义上传 URL - 必须在 django_ckeditor_5.urls 之前！
    path("ckeditor5/image_upload/", blog_views.ckeditor_upload_view, name="ckeditor_upload_view"),
    # 可以保留其他 ckeditor5 功能
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)