from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    # 重写 ready 方法来导入并连接信号
    def ready(self):
        import notifications.signals