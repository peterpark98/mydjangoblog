import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages', # 确保 messages 应用已启用
    'django.contrib.staticfiles',
    'blog',
    'accounts',
    'notifications',
    'django_ckeditor_5',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', # 确保 messages 中间件已启用
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages', # 确保 messages 上下文处理器已启用
                'blog.context_processors.common_data',
                'notifications.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'myblog.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary', # 消息
    messages.INFO: 'alert-info',       # 消息
    messages.SUCCESS: 'alert-success', # 成功
    messages.WARNING: 'alert-warning', # 警告
    messages.ERROR: 'alert-danger',    # 错误
}

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 
            '|', 'imageUpload', 'insertTable', 'mediaEmbed', 'codeBlock', '|', 'undo', 'redo'
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative',
                'imageStyle:alignLeft',
                'imageStyle:alignRight',
                'imageStyle:alignCenter',
                'imageStyle:side',
            ],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ],
            'resizeOptions': [
                { 'name': 'imageResize:original', 'label': '原始大小', 'value': 'null' },
                { 'name': 'imageResize:50', 'label': '50%', 'value': '50' },
                { 'name': 'imageResize:75', 'label': '75%', 'value': '75' },
            ],
            'resizeUnit': 'px',
        },
        'table': {
            'contentToolbar': [
                'tableColumn',
                'tableRow',
                'mergeTableCells'
            ]
        },
        # === 关键配置：自定义 codeBlock 语言 ===
        'codeBlock': {
            'languages': [
                {'language': 'plaintext', 'label': 'Plain Text'},
                {'language': 'python', 'label': 'Python'},
                {'language': 'cpp', 'label': 'C++'},
                {'language': 'bash', 'label': 'Bash/Shell'},
                {'language': 'yaml', 'label': 'YAML'},
                {'language': 'c', 'label': 'C'},
                {'language': 'java', 'label': 'Java'},
                {'language': 'javascript', 'label': 'JavaScript'},
                {'language': 'html', 'label': 'HTML'},
                {'language': 'css', 'label': 'CSS'},
                {'language': 'json', 'label': 'JSON'},
                {'language': 'sql', 'label': 'SQL'},
            ]
        },
        # === 可选：设置默认语言 ===
        'language': 'zh-cn',
        'imageUpload': {
            'backend': 'myblog.image_utils.ckeditor_image_processing',
        },
    },
}

# CKEDITOR_5_IMAGE_PROCESSING_BACKEND = "myblog.image_utils.ckeditor_image_processing"