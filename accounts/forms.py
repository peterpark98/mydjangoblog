from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from .models import Profile
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单，为字段添加样式"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': '请输入您的用户名'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': '请输入您的密码'}
        )

class RegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱地址'})
    )
    nickname = forms.CharField(
        max_length=50,
        required=True,
        label="昵称",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '昵称 (用于显示)'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '账号 (用于登录)'}),
        }
        labels = {
            'username': '账号',
        }
        error_messages = {
            'username': {
                'unique': "已存在一位使用该用户名的用户。",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '密码'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '确认密码'})

    def clean_nickname(self):
        """
        自定义验证方法，检查昵称的唯一性（不区分大小写）。
        """
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname__iexact=nickname).exists():
            raise forms.ValidationError("该昵称已被占用，请换一个。")
        return nickname

    def save(self, commit=True):
        """
        重写 save 方法以正确处理 Profile 的创建和更新。
        """
        # 1. 先调用父类的 save 方法创建用户，但不立即提交到数据库
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        # 2. 如果 commit 为 True，则保存用户
        if commit:
            user.save()
            # 3. 获取由信号自动创建的 Profile 实例，并更新其 nickname
            nickname = self.cleaned_data.get('nickname')
            if nickname:
                # 确保 user.profile 存在
                user.profile.nickname = nickname
                user.profile.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """用户资料更新表单"""
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Profile
        fields = ['nickname', 'bio', 'location', 'birth_date', 'image']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'image': forms.FileInput(attrs={'id': 'id_image', 'class': 'd-none'}),
        }
        labels = {
            'nickname': '昵称',
            'bio': '个人简介',
            'location': '所在地',
            'birth_date': '出生日期',
            'image': '更换头像',
        }
        error_messages = {
            'nickname': {
                'unique': "该昵称已被占用，请换一个。",
            },
        }

    def save(self, commit=True):
        profile = super().save(commit=False)
        image_changed = 'image' in self.changed_data
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        width = self.cleaned_data.get('width')
        height = self.cleaned_data.get('height')

        if image_changed and all(coord is not None for coord in [x, y, width, height]):
            image_file = self.cleaned_data.get('image')
            image = Image.open(image_file)
            cropped_image = image.crop((x, y, x + width, y + height))
            resized_image = cropped_image.resize((300, 300), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image_format = 'PNG' if image.format == 'PNG' else 'JPEG'
            resized_image.save(buffer, format=image_format, quality=90)
            original_file_name = image_file.name
            profile.image.save(original_file_name, ContentFile(buffer.getvalue()), save=False)

        if commit:
            profile.save()
        return profile

class UserUpdateForm(forms.ModelForm):
    """用户信息更新表单"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        labels = {
            'username': '用户名 (登录账号)',
            'email': '邮箱地址',
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """自定义密码修改表单，以添加样式"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': '请输入旧密码'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '请输入新密码'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '请再次输入新密码'})