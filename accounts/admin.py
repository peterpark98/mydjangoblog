from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# 定义一个内联管理界面
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '资料'

# 定义一个新的User管理界面
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nickname', 'location', 'birth_date']